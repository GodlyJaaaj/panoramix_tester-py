# __  __              _____    ______     ____   __     __     _____   ______   ____     ____    _    _
# |  \/  |     /\     |  __ \  |  ____|   |  _ \  \ \   / /    / ____| |  ____| |  _ \   / __ \  | |  | |
# | \  / |    /  \    | |  | | | |__      | |_) |  \ \_/ /    | (___   | |__    | |_) | | |  | | | |  | |
# | |\/| |   / /\ \   | |  | | |  __|     |  _ <    \   /      \___ \  |  __|   |  _ <  | |  | | | |  | |
# | |  | |  / ____ \  | |__| | | |____    | |_) |    | |       ____) | | |____  | |_) | | |__| | | |__| |
# |_|  |_| /_/    \_\ |_____/  |______|   |____/     |_|      |_____/  |______| |____/   \____/   \____/
#

import argparse
import subprocess
import unittest
import random
from colorama import Fore, Style
import concurrent.futures
from typing import Tuple

class TestPanoramix(unittest.TestCase):
    def __init__(self, *test_args, num_tests, max_bound, max_timeout, max_workers=None, **kwargs):
        super().__init__(*test_args, **kwargs)
        self.num_tests = num_tests
        self.max_bound = max_bound
        self.max_timeout = max_timeout
        self.max_workers = max_workers

    def run_single_test(self, test_num: int) -> Tuple[int, bool, str]:
        nb_villagers = random.randint(1, self.max_bound)
        pot_size = random.randint(1, self.max_bound)
        nb_fights = random.randint(1, self.max_bound)
        nb_refills = random.randint(1, self.max_bound)

        p = subprocess.Popen(
            ["./panoramix", str(nb_villagers), str(pot_size),
            str(nb_fights), str(nb_refills)], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        try:
            _, stderr = p.communicate(timeout=self.max_timeout)
            success = True
            message = (f"{Fore.GREEN}Test {test_num + 1} passed: panoramix terminated "
                      f"successfully with parameters ({nb_villagers}, "
                      f"{pot_size}, {nb_fights}, {nb_refills}){Style.RESET_ALL}")
        except subprocess.TimeoutExpired:
            p.kill()
            success = False
            message = (f"{Fore.RED}Test {test_num + 1} failed: panoramix did not "
                      f"terminate with parameters ({nb_villagers}, {pot_size}, "
                      f"{nb_fights}, {nb_refills}){Style.RESET_ALL}")

        return test_num, success, message

    def test_panoramix(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(self.run_single_test, i): i 
                for i in range(self.num_tests)
            }

            failed_tests = []
            for future in concurrent.futures.as_completed(future_to_test):
                test_num, success, message = future.result()
                print(message)
                if not success:
                    failed_tests.append(test_num + 1)

            if failed_tests:
                self.fail(f"Tests failed: {failed_tests}")

def print_args(args):
    print(f"\n{Fore.CYAN}=== Paramètres de test ==={Style.RESET_ALL}")
    print(f"► Nombre de tests : {Fore.YELLOW}{args.num_tests}{Style.RESET_ALL}")
    print(f"► Limite maximale : {Fore.YELLOW}{args.max_bound}{Style.RESET_ALL}")
    print(f"► Timeout maximum : {Fore.YELLOW}{args.max_timeout}s{Style.RESET_ALL}")
    print(f"► Workers maximum : {Fore.YELLOW}{args.max_workers}{Style.RESET_ALL}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("num_tests", type=int, help="Number of tests to run")
    parser.add_argument("max_bound", type=int, help="Max bound for each parameter")
    parser.add_argument("--max_timeout", type=int, default=5, help="Max timeout for each test")
    parser.add_argument("--max_workers", type=int, default=5, help="Maximum number of concurrent tests")
    args = parser.parse_args()
    print_args(args)

    suite = unittest.TestSuite()
    suite.addTest(TestPanoramix('test_panoramix', 
                               num_tests=args.num_tests,
                               max_bound=args.max_bound,
                               max_timeout=args.max_timeout,
                               max_workers=args.max_workers))
    runner = unittest.TextTestRunner()
    runner.run(suite)