import unittest
import asyncio
import re
from odatests import DemoTest

def clean(varStr) -> str:
    return re.sub('\W|^(?=\d)','_', varStr)

class Test_DemoTest(unittest.IsolatedAsyncioTestCase):

    def make_test_function(result):
        def test(self):
            self.assertEqual(True, result)
        return test

    async def run_everything():
        result = await DemoTest.demolist()
        for r in result:
            test_func = Test_DemoTest.make_test_function(r[1])
            setattr(Test_DemoTest, 'test_{0}'.format(clean(r[0])), test_func)

if __name__ == '__main__':
    asyncio.run(Test_DemoTest.run_everything())
    asyncio.run(unittest.main())
