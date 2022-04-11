import unittest
import asyncio
from odatests import DemoTest

class Test_DemoTest(unittest.IsolatedAsyncioTestCase):
    async def test_demotest_results(self):
        result = await DemoTest.demolist()
        self.assertEqual([], result)

if __name__ == '__main__':
    asyncio.run(unittest.main())
