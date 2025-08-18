import unittest
import asyncio
import re
import csv
from odatests import DemoTest

def clean(varStr) -> str:
    return re.sub(r'\W|^(?=\d)', '_', varStr)

class Test_DemoTest(unittest.IsolatedAsyncioTestCase):

    @staticmethod
    def make_test_function(result):
        def test(self):
            self.assertEqual(True, result)
        return test

async def run_everything():
    results = await DemoTest.demolist()
    for r in results:
        test_func = Test_DemoTest.make_test_function(r[1])
        setattr(Test_DemoTest, 'test_{0}'.format(clean(r[0])), test_func)
    
    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    failed = total - passed

    with open("odatests_results_summary.csv", mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["total", "passed", "failed"])
        writer.writeheader()
        writer.writerow({
            "total": total,
            "passed": passed,
            "failed": failed
        })

if __name__ == '__main__':
    asyncio.run(run_everything())
    unittest.main()
