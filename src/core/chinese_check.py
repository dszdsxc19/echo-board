"""Simplified Chinese language compliance checking for Echo-Board."""

import re
from typing import List, Dict, Tuple
from pathlib import Path

from .logging import EchoBoardLogger

logger = EchoBoardLogger.get_logger("chinese_check")


class ChineseLanguageChecker:
    """Check Simplified Chinese language compliance throughout the application."""

    # Common English words that should be translated
    ENGLISH_PATTERNS = [
        r"\b(Setup|Configuration|Settings)\b",
        r"\b(Loading|Load|Save|Delete)\b",
        r"\b(Query|Search|History)\b",
        r"\b(Error|Success|Warning|Failed)\b",
        r"\b(Agent|Response|Advice)\b",
        r"\b(Session|Context|Document)\b",
    ]

    # Required Chinese UI strings
    REQUIRED_CHINESE_STRINGS = [
        "个人董事会",
        "档案管理员",
        "战略顾问",
        "人生教练",
        "设置",
        "笔记目录",
        "加载笔记",
        "对话历史",
        "验证目录",
        "重新索引",
        "向量存储统计",
        "已索引块数",
        "最近更新的文件",
        "查看证据",
        "处理您的查询",
        "正在分析",
        "完成",
        "没有找到相关信息",
        "加载中",
    ]

    @staticmethod
    def check_ui_strings(file_path: str) -> Tuple[bool, List[str]]:
        """Check if UI file contains proper Chinese strings.

        Args:
            file_path: Path to UI file

        Returns:
            Tuple of (is_compliant, list_of_issues)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            issues = []

            # Check for required Chinese strings
            for required in ChineseLanguageChecker.REQUIRED_CHINESE_STRINGS:
                if required not in content:
                    issues.append(f"缺少必需的字符串: {required}")

            # Check for untranslated English
            for pattern in ChineseLanguageChecker.ENGLISH_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues.append(f"发现未翻译的英文: {matches}")

            # Check for user-facing text without Chinese
            st_text_matches = re.findall(r'st\.(title|markdown|header|subheader)\(["\']([^"\']+)["\']', content)
            for func, text in st_text_matches:
                if text and not ChineseLanguageChecker._contains_chinese(text):
                    # Check if it's a technical term or placeholder
                    if not ChineseLanguageChecker._is_technical_term(text):
                        issues.append(f"用户界面文本未翻译: {text}")

            is_compliant = len(issues) == 0
            return is_compliant, issues

        except Exception as e:
            logger.error(f"Error checking UI file {file_path}: {e}")
            return False, [f"检查文件时出错: {str(e)}"]

    @staticmethod
    def check_agent_prompts(prompts_dir: str) -> Tuple[bool, List[str]]:
        """Check if agent prompt files are in Chinese.

        Args:
            prompts_dir: Path to prompts directory

        Returns:
            Tuple of (is_compliant, list_of_issues)
        """
        try:
            prompts_path = Path(prompts_dir)
            if not prompts_path.exists():
                return False, [f"提示词目录不存在: {prompts_dir}"]

            issues = []
            prompt_files = ["archivist.txt", "strategist.txt", "coach.txt"]

            for prompt_file in prompt_files:
                file_path = prompts_path / prompt_file
                if not file_path.exists():
                    issues.append(f"提示词文件不存在: {prompt_file}")
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if prompt contains Chinese
                chinese_ratio = ChineseLanguageChecker._get_chinese_ratio(content)
                if chinese_ratio < 0.7:  # At least 70% should be Chinese
                    issues.append(
                        f"{prompt_file} 中文比例过低: {chinese_ratio:.2%} "
                        f"(至少需要70%)"
                    )

                # Check for English instructions that should be Chinese
                english_instruct_patterns = [
                    r"You are",
                    r"Extract",
                    r"Analyze",
                    r"Provide",
                    r"Based on",
                ]
                for pattern in english_instruct_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(
                            f"{prompt_file} 包含英文指令，请确保为中文提示词"
                        )

            is_compliant = len(issues) == 0
            return is_compliant, issues

        except Exception as e:
            logger.error(f"Error checking prompts: {e}")
            return False, [f"检查提示词时出错: {str(e)}"]

    @staticmethod
    def check_model_strings() -> Tuple[bool, List[str]]:
        """Check if model docstrings and error messages are in Chinese.

        Returns:
            Tuple of (is_compliant, list_of_issues)
        """
        issues = []

        # Check core models
        model_dir = Path("src/core/models")
        if model_dir.exists():
            for model_file in model_dir.glob("*.py"):
                with open(model_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for English error messages
                error_matches = re.findall(r'raise \w+Error\(["\']([^"\']+)["\']', content)
                for error_msg in error_matches:
                    if not ChineseLanguageChecker._contains_chinese(error_msg):
                        issues.append(f"{model_file.name} 错误信息未翻译: {error_msg}")

                # Check for English docstrings
                docstring_matches = re.findall(r'def\s+\w+\([^)]*\):\s*"""([^"]+)"""', content)
                for docstring in docstring_matches:
                    if len(docstring) > 50 and not ChineseLanguageChecker._contains_chinese(docstring):
                        issues.append(f"{model_file.name} 文档字符串未翻译")

        is_compliant = len(issues) == 0
        return is_compliant, issues

    @staticmethod
    def run_full_compliance_check() -> Dict[str, Tuple[bool, List[str]]]:
        """Run full Chinese language compliance check.

        Returns:
            Dictionary with check results for each component
        """
        logger.info("Starting full Chinese language compliance check")

        results = {}

        # Check UI strings
        ui_files = [
            "src/app.py",
        ]
        for ui_file in ui_files:
            if Path(ui_file).exists():
                is_compliant, issues = ChineseLanguageChecker.check_ui_strings(ui_file)
                results[ui_file] = (is_compliant, issues)
                logger.info(f"Checked {ui_file}: {'✅' if is_compliant else '❌'}")

        # Check agent prompts
        prompts_dir = "src/agents/prompts"
        if Path(prompts_dir).exists():
            is_compliant, issues = ChineseLanguageChecker.check_agent_prompts(prompts_dir)
            results[prompts_dir] = (is_compliant, issues)
            logger.info(f"Checked {prompts_dir}: {'✅' if is_compliant else '❌'}")

        # Check model strings
        is_compliant, issues = ChineseLanguageChecker.check_model_strings()
        results["models"] = (is_compliant, issues)
        logger.info(f"Checked models: {'✅' if is_compliant else '❌'}")

        # Summary
        total_issues = sum(len(result[1]) for result in results.values())
        if total_issues == 0:
            logger.info("✅ 所有组件都符合中文语言要求")
        else:
            logger.warning(f"❌ 发现 {total_issues} 个中文语言合规问题")

        return results

    @staticmethod
    def _contains_chinese(text: str) -> bool:
        """Check if text contains Chinese characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Chinese characters
        """
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        return bool(chinese_pattern.search(text))

    @staticmethod
    def _get_chinese_ratio(text: str) -> float:
        """Get ratio of Chinese characters in text.

        Args:
            text: Text to analyze

        Returns:
            Ratio of Chinese characters (0.0 to 1.0)
        """
        if not text:
            return 0.0

        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        total_chars = len(text)
        return chinese_chars / total_chars if total_chars > 0 else 0.0

    @staticmethod
    def _is_technical_term(text: str) -> bool:
        """Check if text is a technical term that doesn't need translation.

        Args:
            text: Text to check

        Returns:
            True if text is a technical term
        """
        technical_terms = [
            "API",
            "LLM",
            "JSON",
            "UUID",
            "HTML",
            "SQL",
            "CSS",
            "async",
            "await",
            "lambda",
            "git",
            "http",
            "https",
        ]
        return any(term in text for term in technical_terms)


def main():
    """Main function to run compliance check."""
    print("=" * 60)
    print("Simplified Chinese Language Compliance Check")
    print("=" * 60)
    print()

    results = ChineseLanguageChecker.run_full_compliance_check()

    print("\n" + "=" * 60)
    print("Compliance Report")
    print("=" * 60)

    for component, (is_compliant, issues) in results.items():
        print(f"\n{component}:")
        if is_compliant:
            print("  ✅ Compliant")
        else:
            print("  ❌ Non-compliant")
            for issue in issues:
                print(f"    - {issue}")

    total_issues = sum(len(result[1]) for result in results.values())
    print("\n" + "=" * 60)
    if total_issues == 0:
        print("✅ All components are compliant!")
    else:
        print(f"❌ Found {total_issues} compliance issues")
    print("=" * 60)
