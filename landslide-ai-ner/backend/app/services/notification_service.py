"""
Multilingual Notification and Translation Service.
Supports English, Hindi, Assamese, and Bengali translations for early warning dispatches.
"""
from typing import Dict, Any

TEMPLATES = {
    "en": {
        "HIGH": "Landslide risk has increased in {location}. Current risk level: HIGH. Authorities and residents are advised to monitor official guidance and avoid unnecessary travel in vulnerable areas.",
        "VERY_HIGH": "Very High landslide risk detected near {location}. Unstable slope conditions. Evacuate vulnerable structures as advised by local disaster authority.",
        "CRITICAL": "CRITICAL landslide risk indication detected near {location}. High probability of slope failure. Follow instructions from local authorities and disaster-management agencies immediately.",
        "disclaimer": "This is an AI-generated decision-support risk indication. Official disaster-management guidance takes precedence.",
    },
    "hi": {
        "HIGH": "{location} में भूस्खलन का जोखिम बढ़ गया है। वर्तमान जोखिम स्तर: उच्च (HIGH)। अधिकारियों और नागरिकों को आधिकारिक दिशा-निर्देशों का पालन करने और संवेदनशील क्षेत्रों में यात्रा से बचने की सलाह दी जाती है।",
        "VERY_HIGH": "{location} के पास बहुत अधिक (VERY HIGH) भूस्खलन जोखिम का पता चला है। ढलान अस्थिर है। स्थानीय आपदा प्रबंधन के निर्देशानुसार सुरक्षित स्थान पर जाएं।",
        "CRITICAL": "{location} के पास गंभीर (CRITICAL) भूस्खलन जोखिम का संकेत मिला है। तत्काल स्थानीय प्रशासन और आपदा प्रबंधन एजेंसियों के निर्देशों का पालन करें।",
        "disclaimer": "यह एक AI-जनित निर्णय-समर्थन जोखिम संकेत है। आधिकारिक आपदा प्रबंधन निर्देश ही सर्वोपरि हैं।",
    },
    "as": {
        "HIGH": "{location} ত ভূমিস্খলনৰ সম্ভাৱনা বৃদ্ধি পাইছে। বৰ্তমান বিপদ স্তৰ: উচ্চ (HIGH)। জিলা প্ৰশাসন আৰু ৰাইজক সতৰ্ক থাকিবলৈ আৰু জৰুৰী নহ'লে যাত্ৰা পৰিহাৰ কৰিবলৈ অনুৰোধ জনোৱা হৈছে।",
        "VERY_HIGH": "{location} ৰ ওচৰত অতি উচ্চ (VERY HIGH) ভূমিস্খলনৰ আশংকা দেখা গৈছে। পাহাৰীয়া ঢাল অস্থিৰ। দুৰ্যোগ প্ৰশমন বিভাগৰ নিৰ্দেশনা অনুসৰণ কৰক।",
        "CRITICAL": "{location} ৰ ওচৰত অত্যন্ত সংকটজনক (CRITICAL) ভূমিস্খলনৰ বিপদ সংকেত। তাৎক্ষণিকভাৱে সুৰক্ষিত স্থানলৈ যাওক আৰু প্ৰশাসনৰ নিৰ্দেশ মানি চলক।",
        "disclaimer": "এইটো এটা AI-ভিত্তিক পূৰ্বাভাস। চৰকাৰী দুৰ্যোগ ব্যৱস্থাপনা কৰ্তৃপক্ষৰ নিৰ্দেশনাই চূড়ান্ত।",
    },
    "bn": {
        "HIGH": "{location}-এ ভূমিধসের ঝুঁকি বৃদ্ধি পেয়েছে। বর্তমান ঝুঁকির মাত্রা: উচ্চ (HIGH)। প্রশাসন এবং নাগরিকদের সতর্ক থাকার এবং ঝুঁকিপূর্ণ এলাকায় যাতায়াত এড়ানোর পরামর্শ দেওয়া হচ্ছে।",
        "VERY_HIGH": "{location}-এর কাছে অত্যন্ত উচ্চ (VERY HIGH) ভূমিধসের ঝুঁকি চিহ্নিত হয়েছে। স্থানীয় দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষের নির্দেশ মেনে চলুন।",
        "CRITICAL": "{location}-এর কাছে সংকটজনক (CRITICAL) ভূমিধস ঝুঁকি সংকেত। অবিলম্বে নিরাপদ আশ্রয়ে যান এবং প্রশাসনের নির্দেশাবলী অনুসরণ করুন।",
        "disclaimer": "এটি একটি এআই-ভিত্তিক সিদ্ধান্ত-সহায়ক ঝুঁকি নির্দেশক। সরকারি দুর্যোগ ব্যবস্থাপনা নির্দেশনাই চূড়ান্ত।",
    }
}


class NotificationService:
    """Format emergency messages in localized languages."""

    def format_alert_message(self, risk_level: str, location_name: str, language: str = "en") -> str:
        lang = language if language in TEMPLATES else "en"
        tmpl_dict = TEMPLATES.get(lang, TEMPLATES["en"])
        base_msg = tmpl_dict.get(risk_level, tmpl_dict.get("HIGH", ""))
        formatted_body = base_msg.format(location=location_name)
        disclaimer = tmpl_dict.get("disclaimer", TEMPLATES["en"]["disclaimer"])
        return f"{formatted_body}\n\n[{disclaimer}]"


notification_service = NotificationService()
