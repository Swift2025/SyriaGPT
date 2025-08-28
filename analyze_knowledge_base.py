#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تحليل شاملة لقاعدة المعرفة السورية
أداة مفيدة لمراقبة وتحليل حالة قاعدة المعرفة بشكل دوري
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class KnowledgeBaseAnalyzer:
    def __init__(self):
        self.data_dir = Path("data/syria_knowledge")
        
    def analyze_all_files(self) -> Dict[str, Any]:
        """تحليل جميع ملفات قاعدة المعرفة"""
        print("🔍 بدء تحليل قاعدة المعرفة السورية...")
        
        analysis_results = {
            "files": {},
            "total_questions": 0,
            "categories": {},
            "quality_metrics": {},
            "compliance_check": {},
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # تحليل كل ملف
        for json_file in self.data_dir.glob("*.json"):
            if json_file.name == "analyze_knowledge_base.py":
                continue
            file_analysis = self.analyze_single_file(json_file)
            analysis_results["files"][json_file.name] = file_analysis
            analysis_results["total_questions"] += file_analysis["total_questions"]
            
            # تجميع الإحصائيات حسب الفئة
            category = file_analysis.get("category", "unknown")
            if category not in analysis_results["categories"]:
                analysis_results["categories"][category] = 0
            analysis_results["categories"][category] += file_analysis["total_questions"]
        
        # تحليل جودة البيانات
        analysis_results["quality_metrics"] = self.analyze_quality(analysis_results["files"])
        
        # فحص التوافق مع المتطلبات
        analysis_results["compliance_check"] = self.check_compliance(analysis_results)
        
        return analysis_results
    
    def analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """تحليل ملف واحد"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = {
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "total_questions": len(data.get("qa_pairs", [])),
                "category": data.get("category", "unknown"),
                "description": data.get("description", ""),
                "version": data.get("version", "unknown"),
                "generated_at": data.get("generated_at", ""),
                "qa_pairs_analysis": self.analyze_qa_pairs(data.get("qa_pairs", [])),
                "structure_compliance": self.check_structure_compliance(data)
            }
            
            return analysis
            
        except Exception as e:
            return {
                "file_name": file_path.name,
                "error": str(e),
                "total_questions": 0
            }
    
    def analyze_qa_pairs(self, qa_pairs: List[Dict]) -> Dict[str, Any]:
        """تحليل أزواج الأسئلة والأجوبة"""
        if not qa_pairs:
            return {"error": "No QA pairs found"}
        
        analysis = {
            "total_pairs": len(qa_pairs),
            "avg_question_variants": 0,
            "avg_answer_length": 0,
            "avg_keywords_count": 0,
            "confidence_distribution": {},
            "source_distribution": {},
            "language_distribution": {"arabic": 0, "english": 0, "mixed": 0}
        }
        
        total_variants = 0
        total_answer_length = 0
        total_keywords = 0
        
        for qa in qa_pairs:
            # عدد متغيرات السؤال
            variants = len(qa.get("question_variants", []))
            total_variants += variants
            
            # طول الإجابة
            answer_length = len(qa.get("answer", ""))
            total_answer_length += answer_length
            
            # عدد الكلمات المفتاحية
            keywords_count = len(qa.get("keywords", []))
            total_keywords += keywords_count
            
            # توزيع مستوى الثقة
            confidence = qa.get("confidence", 0)
            if confidence not in analysis["confidence_distribution"]:
                analysis["confidence_distribution"][confidence] = 0
            analysis["confidence_distribution"][confidence] += 1
            
            # توزيع المصادر
            source = qa.get("source", "unknown")
            if source not in analysis["source_distribution"]:
                analysis["source_distribution"][source] = 0
            analysis["source_distribution"][source] += 1
            
            # تحليل اللغة
            question_text = " ".join(qa.get("question_variants", []))
            answer_text = qa.get("answer", "")
            if self.contains_arabic(question_text) and self.contains_english(question_text):
                analysis["language_distribution"]["mixed"] += 1
            elif self.contains_arabic(question_text):
                analysis["language_distribution"]["arabic"] += 1
            else:
                analysis["language_distribution"]["english"] += 1
        
        # حساب المتوسطات
        if analysis["total_pairs"] > 0:
            analysis["avg_question_variants"] = total_variants / analysis["total_pairs"]
            analysis["avg_answer_length"] = total_answer_length / analysis["total_pairs"]
            analysis["avg_keywords_count"] = total_keywords / analysis["total_pairs"]
        
        return analysis
    
    def contains_arabic(self, text: str) -> bool:
        """التحقق من وجود نص عربي"""
        arabic_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئ')
        return any(char in arabic_chars for char in text)
    
    def contains_english(self, text: str) -> bool:
        """التحقق من وجود نص إنجليزي"""
        english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return any(char in english_chars for char in text)
    
    def check_structure_compliance(self, data: Dict) -> Dict[str, bool]:
        """فحص توافق البنية مع المتطلبات"""
        compliance = {
            "has_category": "category" in data,
            "has_description": "description" in data,
            "has_qa_pairs": "qa_pairs" in data,
            "qa_pairs_is_list": isinstance(data.get("qa_pairs"), list),
            "has_total_questions": "total_questions" in data
        }
        
        # فحص بنية أزواج الأسئلة والأجوبة
        if "qa_pairs" in data and isinstance(data["qa_pairs"], list):
            sample_qa = data["qa_pairs"][0] if data["qa_pairs"] else {}
            compliance.update({
                "qa_has_id": "id" in sample_qa,
                "qa_has_question_variants": "question_variants" in sample_qa,
                "qa_has_answer": "answer" in sample_qa,
                "qa_has_keywords": "keywords" in sample_qa,
                "qa_has_confidence": "confidence" in sample_qa,
                "qa_has_source": "source" in sample_qa
            })
        
        return compliance
    
    def analyze_quality(self, files_analysis: Dict) -> Dict[str, Any]:
        """تحليل جودة البيانات"""
        quality_metrics = {
            "overall_quality_score": 0,
            "structure_quality": 0,
            "content_quality": 0,
            "language_quality": 0,
            "issues": []
        }
        
        total_files = len(files_analysis)
        structure_score = 0
        content_score = 0
        language_score = 0
        
        for file_name, analysis in files_analysis.items():
            if "error" in analysis:
                quality_metrics["issues"].append(f"Error in {file_name}: {analysis['error']}")
                continue
            
            # تقييم البنية
            compliance = analysis.get("structure_compliance", {})
            structure_score += sum(compliance.values()) / len(compliance) if compliance else 0
            
            # تقييم المحتوى
            qa_analysis = analysis.get("qa_pairs_analysis", {})
            if qa_analysis.get("total_pairs", 0) > 0:
                content_score += 1  # وجود أسئلة وأجوبة
                if qa_analysis.get("avg_answer_length", 0) > 20:
                    content_score += 1  # إجابات مفصلة
                if qa_analysis.get("avg_keywords_count", 0) > 2:
                    content_score += 1  # كلمات مفتاحية كافية
            
            # تقييم اللغة
            lang_dist = qa_analysis.get("language_distribution", {})
            if lang_dist.get("arabic", 0) > 0:
                language_score += 1  # وجود محتوى عربي
            if lang_dist.get("mixed", 0) > 0:
                language_score += 1  # وجود محتوى ثنائي اللغة
        
        # حساب النقاط النهائية
        if total_files > 0:
            quality_metrics["structure_quality"] = structure_score / total_files
            quality_metrics["content_quality"] = content_score / (total_files * 3)  # 3 معايير للمحتوى
            quality_metrics["language_quality"] = language_score / (total_files * 2)  # 2 معايير للغة
            quality_metrics["overall_quality_score"] = (
                quality_metrics["structure_quality"] * 0.3 +
                quality_metrics["content_quality"] * 0.4 +
                quality_metrics["language_quality"] * 0.3
            )
        
        return quality_metrics
    
    def check_compliance(self, analysis_results: Dict) -> Dict[str, Any]:
        """فحص التوافق مع المتطلبات الأصلية"""
        compliance = {
            "meets_quantity_requirement": False,
            "meets_structure_requirement": False,
            "meets_quality_requirement": False,
            "overall_compliance": False,
            "recommendations": []
        }
        
        total_questions = analysis_results["total_questions"]
        
        # فحص متطلب الكمية (500-1000 سؤال)
        if 500 <= total_questions <= 1000:
            compliance["meets_quantity_requirement"] = True
        elif total_questions > 1000:
            compliance["meets_quantity_requirement"] = True
            compliance["recommendations"].append("تم تجاوز الحد الأقصى المطلوب - ممتاز!")
        else:
            compliance["recommendations"].append(f"نحتاج {500 - total_questions} سؤال إضافي للوصول للحد الأدنى")
        
        # فحص متطلب البنية
        required_files = ["cities.json", "government.json", "culture.json", "economy.json", "general.json"]
        existing_files = list(analysis_results["files"].keys())
        missing_files = [f for f in required_files if f not in existing_files]
        
        if not missing_files:
            compliance["meets_structure_requirement"] = True
        else:
            compliance["recommendations"].append(f"الملفات المفقودة: {missing_files}")
        
        # فحص متطلب الجودة
        quality_score = analysis_results["quality_metrics"]["overall_quality_score"]
        if quality_score >= 0.8:
            compliance["meets_quality_requirement"] = True
        else:
            compliance["recommendations"].append(f"تحسين الجودة المطلوب - النتيجة الحالية: {quality_score:.2f}")
        
        # التوافق العام
        compliance["overall_compliance"] = (
            compliance["meets_quantity_requirement"] and
            compliance["meets_structure_requirement"] and
            compliance["meets_quality_requirement"]
        )
        
        return compliance
    
    def generate_report(self, analysis_results: Dict) -> str:
        """إنشاء تقرير شامل"""
        report = []
        report.append("=" * 60)
        report.append("📊 تقرير تحليل قاعدة المعرفة السورية")
        report.append("=" * 60)
        
        # تاريخ التحليل
        report.append(f"\n📅 تاريخ التحليل: {analysis_results.get('analysis_date', 'غير محدد')}")
        
        # ملخص عام
        report.append(f"\n🎯 إجمالي الأسئلة: {analysis_results['total_questions']}")
        report.append(f"📁 عدد الملفات: {len(analysis_results['files'])}")
        
        # تحليل الملفات
        report.append("\n📄 تحليل الملفات:")
        for file_name, analysis in analysis_results["files"].items():
            if "error" in analysis:
                report.append(f"  ❌ {file_name}: خطأ - {analysis['error']}")
            else:
                report.append(f"  ✅ {file_name}: {analysis['total_questions']} سؤال")
        
        # تحليل الفئات
        report.append("\n📂 تحليل الفئات:")
        for category, count in analysis_results["categories"].items():
            report.append(f"  📁 {category}: {count} سؤال")
        
        # تحليل الجودة
        quality = analysis_results["quality_metrics"]
        report.append(f"\n🔍 تحليل الجودة:")
        report.append(f"  📊 جودة البنية: {quality['structure_quality']:.2f}")
        report.append(f"  📊 جودة المحتوى: {quality['content_quality']:.2f}")
        report.append(f"  📊 جودة اللغة: {quality['language_quality']:.2f}")
        report.append(f"  📊 الجودة الإجمالية: {quality['overall_quality_score']:.2f}")
        
        # فحص التوافق
        compliance = analysis_results["compliance_check"]
        report.append(f"\n✅ فحص التوافق مع المتطلبات:")
        report.append(f"  📊 متطلب الكمية (500-1000): {'✅' if compliance['meets_quantity_requirement'] else '❌'}")
        report.append(f"  📊 متطلب البنية: {'✅' if compliance['meets_structure_requirement'] else '❌'}")
        report.append(f"  📊 متطلب الجودة: {'✅' if compliance['meets_quality_requirement'] else '❌'}")
        report.append(f"  📊 التوافق العام: {'✅' if compliance['overall_compliance'] else '❌'}")
        
        # التوصيات
        if compliance["recommendations"]:
            report.append(f"\n💡 التوصيات:")
            for rec in compliance["recommendations"]:
                report.append(f"  💡 {rec}")
        
        # النتيجة النهائية
        if compliance["overall_compliance"]:
            report.append(f"\n🎉 النتيجة: قاعدة المعرفة متوافقة مع جميع المتطلبات!")
        else:
            report.append(f"\n⚠️ النتيجة: قاعدة المعرفة تحتاج تحسينات")
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """الدالة الرئيسية"""
    print("🔍 أداة تحليل قاعدة المعرفة السورية")
    print("=" * 50)
    
    analyzer = KnowledgeBaseAnalyzer()
    analysis_results = analyzer.analyze_all_files()
    
    # إنشاء التقرير
    report = analyzer.generate_report(analysis_results)
    print(report)
    
    # حفظ التقرير في ملف ثابت
    report_file = Path("knowledge_base_analysis_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 تم حفظ التقرير في: {report_file}")
    print(f"💡 يمكنك تشغيل هذا السكريبت في أي وقت لمراقبة حالة قاعدة المعرفة")
    print(f"📝 الملف سيتم تحديثه في كل مرة تشغل فيها السكريبت")
    
    return analysis_results

if __name__ == "__main__":
    main()
