import sys
import os
import pytest
from collections import defaultdict


from _pytest.terminal import TerminalReporter
from _pytest import python


class VPLReporter(TerminalReporter):
    def __init__(self, config):
        super().__init__(config)
        self._failed = defaultdict(list)
        self._passed = defaultdict(list)
        self._collected = defaultdict(list)
        self._collected_failed = []
        self._score = {}

    def pytest_exception_interact(self, node, call, report):
        if hasattr(call.excinfo, "_excinfo"):
            exception = call.excinfo._excinfo[1]
            while exception.__cause__ is not None:
                exception = exception.__cause__

            traceback = exception.__traceback__
            while traceback.tb_next is not None:
                traceback = traceback.tb_next

            report._exception = exception
            report._traceback = traceback

    def _report_keyboardinterrupt(self) -> None:
        pass

    def write_fspath_result(self, nodeid: str, res: str) -> None:
        pass

    def pytest_sessionstart(self, session):
        self._session = session

    def pytest_sessionfinish(self, session, exitstatus):
        total_score = sum(v for v in self._score.values())
        if len(self._passed) > 0:
            self.write_line("")
            self.write_line("<|--")
            if len(self._passed) == len(self._collected):
                self.write_line("✨ Congratulations! All tests have passed! ✨")
                self.write_line(
                    "🎉 Excellent work! You've successfully completed all the requirements!"
                )
                if any(
                    p.suggestions for passed in self._passed.values() for p in passed
                ):
                    self.write_line("")
                    self.write_line(
                        "Please take a look at these suggestions to improve your solution"
                    )
                    for family, passed in self._passed.items():
                        for p in passed:
                            if p.suggestions:
                                self.write_line(f"✅ {p.description}")
                                for suggestion in p.suggestions:
                                    self.write_line(f"⠀💡{suggestion}")
            else:
                self.write_line("🌟 Passing tests  🎯")
                self.write_line(
                    "These tests passed successfully! 💪 "
                    "Keep going - you're making great progress 🚀"
                )
                self.write_line("")
                for family, passed in self._passed.items():
                    for p in passed:
                        self.write_line(f"✅ {p.description}")
                        if p.suggestions:
                            for suggestion in p.suggestions:
                                self.write_line(f"⠀💡{suggestion}")

            self.write_line("")
            self.write_line("--|>")

        if len(self._failed) > 0:
            self.write_line("")
            self.write_line("<|--")
            self.write_line("⚠️ Failing tests ❌")
            self.write_line(
                f"💪 Keep going! {len(self._failed)} test(s) still need work, "
                "but you're making progress!"
            )
            self.write_line(
                "💡 Check the details below for hints to improve your solution."
            )
            self.write_line("")
            for family, results in self._failed.items():
                total_score -= self._score[family]
                for failed in results:
                    self.write_line(f"❌ {failed.description}")
                    for suggestion in failed.suggestions:
                        self.write_line(f"⠀💡{suggestion}")

                    if failed.longrepr:
                        if isinstance(failed.longrepr, tuple):
                            self.write_line(
                                "💡 Oops! Test skipping isn't part of the journey! "
                            )
                            self.write_line(
                                "Let's tackle each test together - you've got this! 💪"
                            )
                        else:
                            if not self.config.hide_assert:
                                for trace in failed.longrepr.chain:
                                    for entry in trace[0].reprentries:
                                        for line in entry.lines:
                                            if line.startswith(">") or line.startswith(
                                                "E"
                                            ):
                                                self.write_line(f"> {line}")
                    self.write_line("")
            self.write_line("--|>")

        if hasattr(session.config, "grade_formatter"):
            total_score = session.config.grade_formatter(total_score)

        self.write_line(f"Grade :=>> {total_score}")

    def pytest_collection_finish(self, session):
        if len(self._collected_failed) > 0:
            self.write_line("")
            self.write_line("<|--")

            self.write_line("⚠️ Code Compilation Issues")
            self.write_line(
                "💡 Almost there! Let's fix these compilation errors and get your code running:"
            )
            self.write_line("")
            for report in self._collected_failed:
                if hasattr(report, "_traceback") and hasattr(report, "_exception"):
                    tb = report._traceback
                    ex = report._exception
                    filename = os.path.basename(tb.tb_frame.f_code.co_filename)
                    lineno = tb.tb_lineno
                    self.write_line(f"⚠️ {filename}:{lineno}")

                    for line in str(ex).splitlines():
                        self.write_line(f"> {line}")
                else:
                    self.write_line("⚠️ Unknown error, see traceback")
                    message = str(report.longrepr)
                    for line in message.splitlines():
                        self.write_line(f"> {line}")

            self.write_line("")
            self.write_line("--|>")
            return

        self.write_line("<|--")
        self.write_line(
            "🎯 Let's check your solution! Here are the tests we'll run: ✨"
        )
        self.write_line("")
        for family, results in self._collected.items():
            score = self._score[family]
            render = []
            for func in results:
                description = func._obj.__doc__
                if description:
                    description = description.strip()
                    if hasattr(func, "callspec"):
                        description = description.format(**func.callspec.params)
                else:
                    description = func.originalname

                func._description = description
                render.append(description)

            if len(render) > 1:
                self.write_line(
                    f"📝 {len(render)} test configurations worth {score} point(s)"
                )
                for r in render:
                    self.write_line(f"⠀⠀↪️ {r}")
            else:
                self.write_line(f"📝 {render[0]} worth {score} point(s)")
        self.write_line("")
        self.write_line("--|>")

    def pytest_collection(self):
        pass

    def pytest_collectreport(self, report):
        if report.failed:
            self._collected_failed.append(report)
        else:
            if report.nodeid != "":
                for result in report.result:
                    if not isinstance(result, python.Class):
                        marker = result.get_closest_marker("score")
                        self._score[result.originalname] = (
                            marker.args[0] if marker else 1
                        )
                        self._collected[result.originalname].append(result)

    def summary_stats(self):
        return

    def short_test_summary(self):
        pass

    def report_collect(self, final: bool = False) -> None:
        pass

    def summary_failures(self) -> None:
        pass

    def summary_xfailures(self):
        pass

    def summary_errors(self) -> None:
        pass

    def summary_warnings(self) -> None:
        pass

    def summary_passes(self) -> None:
        pass

    def show_skipped(self):
        pass

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.outcome == "passed":
                self._passed[report.originalname].append(report)
            else:
                self._failed[report.originalname].append(report)


class VPLPlugin:
    @staticmethod
    @pytest.hookimpl(trylast=True)
    def pytest_configure(config):
        if config.pluginmanager.has_plugin("terminalreporter"):
            reporter = config.pluginmanager.get_plugin("terminalreporter")
            config.pluginmanager.unregister(reporter, "terminalreporter")

            reporter = VPLReporter(config)
            config.pluginmanager.register(reporter, "terminalreporter")

        if not hasattr(config, "hide_assert"):
            config.hide_assert = False

    @staticmethod
    def pytest_runtest_call(item):
        class VPL:
            def suggest(self, condition, message):
                if condition:
                    item._suggestions.append(message)

            def try_import(self, module):
                import importlib

                try:
                    return importlib.import_module(module)
                except Exception:
                    return None

        vpl = VPL()
        item._suggestions = []
        if hasattr(item, "_obj") and item._obj is not None:
            item._obj.__globals__["vpl"] = vpl
        if hasattr(item, "_instance") and item._instance is not None:
            item._obj.__globals__["vpl"] = vpl

    @staticmethod
    def pytest_runtest_makereport(item, call):
        report = pytest.TestReport.from_item_and_call(item, call)
        report.description = item._description
        report.originalname = item.originalname
        if call.when == "call":
            report.suggestions = item._suggestions
        else:
            report.suggestions = []

        return report


def main():
    sys.exit(pytest.main(sys.argv[1:], plugins=[VPLPlugin()]))


if __name__ == "__main__":
    main()
