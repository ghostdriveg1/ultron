import asyncio
import hashlib

from packages.infrastructure.redis_client import UltronRedis
from .whitelist_enforcer import WhitelistEnforcer
from .evaluator import AlphaEvaluator
from .crossover import PromptCrossover
from .canary_deployer import CanaryDeployer
from packages.entropy_engine.engine import EntropyEngine

# Phase 5 Real Dependences
from packages.brain.key_rotation.provider_clients import GeminiClient
from packages.brain.puter_opus_caller import PuterOpusCaller
from packages.tools.code.tester_tool import TesterTool
from packages.tools.code.linter_tool import LinterTool
from packages.execution.e2b_manager import E2BSandboxManager

class Evolver:
    """Main coordinator for the AlphaEvolve genetic algorithm loop."""
    
    def __init__(self, redis: UltronRedis, entropy_engine: EntropyEngine):
        self.redis = redis
        self.entropy_engine = entropy_engine
        self.enforcer = WhitelistEnforcer()
        self.evaluator = AlphaEvaluator()
        self.crossover = PromptCrossover()
        self.canary = CanaryDeployer(redis)
        self._task = None
        
        self.gemini = GeminiClient()
        self.opus_caller = PuterOpusCaller(redis, None)
        self.tester = TesterTool()
        self.linter = LinterTool()
        self.e2b = E2BSandboxManager()
        
        self.best_score = 0.0
        self.stagnant_epochs = 0

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._evolution_loop())

    async def _evaluate_variant(self, variant: str, target_file: str) -> float:
        """5-metric real evaluation."""
        import os
        
        # 1. TesterTool (100% pass)
        test_result = await self.tester.execute({"file_path": target_file})
        tests_score = 20.0 if "100% pass" in str(test_result) else 0.0
        
        # 2. EntropyEngine.compute_task_entropy
        entropy_val = await self.entropy_engine.compute_task_entropy({"file": target_file, "content": variant})
        entropy_score = max(0, 20.0 - (entropy_val * 10))
        
        # 3. E2BSandboxManager perf(100it)
        perf_res = await self.e2b.run_code(variant, iterations=100)
        perf_score = min(20.0, 1000.0 / (perf_res.get('latency_ms', 50) + 1))
        
        # 4. LinterTool pylint
        linter_res = await self.linter.execute({"file_path": target_file, "content": variant})
        pylint_score = 20.0 if "0 errors" in str(linter_res).lower() else 5.0
        
        # 5. Gemini style vs skills/*.md
        api_key = os.environ.get("GEMINI_KEY_1", "")
        style_prompt = f"Evaluate this code style against skills/*.md patterns. Code:\n{variant}\nScore 0-20."
        style_res = await self.gemini.generate(prompt=style_prompt, model="gemini-2.5-flash", api_key=api_key)
        try:
            style_score = float(style_res.content.strip())
        except:
            style_score = 10.0
            
        total = tests_score + entropy_score + perf_score + pylint_score + style_score
        return float(total)

    async def _generate_10_variants(self, base_prompt: str, target_file: str) -> list:
        """Parallel generation via Gemini Flash."""
        import os
        api_key = os.environ.get("GEMINI_KEY_1", "")
        
        async def _gen_variant(i: int):
            prompt = f"Optimize this code. Variant {i} characteristics: high temp. Code:\n{base_prompt}"
            res = await self.gemini.generate(prompt=prompt, model="gemini-2.5-flash", api_key=api_key)
            variant = res.content
            score = await self._evaluate_variant(variant, target_file)
            return {"text": variant, "score": score, "id": f"var_{i}"}
            
        variants = await asyncio.gather(*[_gen_variant(i) for i in range(10)])
        return list(variants)

    async def _evolution_loop(self):
        while True:
            try:
                target_file = self.entropy_engine.identify_weakest_component()
                print(f"AlphaEvolve Targeting: {target_file}")
                
                if self.enforcer.is_allowed(target_file):
                    try:
                        with open(target_file, "r") as f:
                            base_prompt = f.read()
                    except FileNotFoundError:
                        base_prompt = "# Target file not found "
                        
                    variants = await self._generate_10_variants(base_prompt, target_file)
                    variants.sort(key=lambda x: x["score"], reverse=True)
                    top_3 = variants[:3]
                    
                    # top3 crossover -> 5 hybrids -> reeval
                    hybrids = []
                    for i in range(5):
                        p1 = top_3[i % 3]["text"]
                        p2 = top_3[(i + 1) % 3]["text"]
                        hybrid_text = self.crossover.blend_prompts(p1, p2)
                        hybrid_score = await self._evaluate_variant(hybrid_text, target_file)
                        hybrids.append({"text": hybrid_text, "score": hybrid_score})
                        
                    all_candidates = top_3 + hybrids
                    all_candidates.sort(key=lambda x: x["score"], reverse=True)
                    best_candidate = all_candidates[0]
                    current_best = best_candidate["score"]
                    
                    # converge (>2% improv / 10 gens / Opus optimal)
                    if current_best <= self.best_score * 1.02:
                        self.stagnant_epochs += 1
                        if self.stagnant_epochs >= 10:
                            print("Convergence reached. Calling Opus optimal...")
                            opus_res = await self.opus_caller.call(prompt=f"Final optimal pass for:\n{best_candidate['text']}")
                            best_candidate["text"] = opus_res
                            self.stagnant_epochs = 0 # reset
                    else:
                        self.best_score = current_best
                        self.stagnant_epochs = 0
                    
                    mutation_id = f"mut_{hashlib.md5(best_candidate['text'].encode()).hexdigest()[:8]}"
                    await self.redis.set(f"mutation:{mutation_id}", best_candidate["text"])
                    
                    print(f"Deploying Canary {mutation_id}")
                    await self.canary.deploy_canary(mutation_id, 5)
                    # monitor(3600s)
                    metrics = await self.canary.gather_metrics(mutation_id, 3600)
                    score = await self.evaluator.evaluate_fitness(mutation_id, metrics)
                    
                    if score > 80.0:
                        print(f"Promoting {mutation_id} to mainline.")
                    else:
                        print(f"Rolling back {mutation_id}. Final score {score} too low.")
                        
            except Exception as e:
                print(f"Evolver error: {e}")
                
            await asyncio.sleep(3600)

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
