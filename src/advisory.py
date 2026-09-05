"""
FasalRakshak - Multilingual Agricultural Advisory & Translation Engine
Provides full-text translations for disease diagnosis, organic remedies,
chemical treatments, and prevention guidelines in 10 Indian regional languages + English.
Integrates with Sarvam AI bulbul TTS for regional neural voice announcements.
"""

import os
import json
import base64
import requests
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from src.rag_engine import AgriculturalRAGEngine

# Master Crop Translations for All 10 Supported Languages
CROP_TRANSLATIONS = {
    "Apple": {
        "English": "Apple", "Hindi": "सेब", "Khortha": "सेब", "Nagpuri": "सेब", "Bhojpuri": "सेब",
        "Bengali": "আপেল", "Marathi": "सफरचंद", "Telugu": "ఆపిల్", "Tamil": "ஆப்பிள்", "Gujarati": "સફરજન", "Punjabi": "ਸੇਬ"
    },
    "Blueberry": {
        "English": "Blueberry", "Hindi": "ब्लूबेरी", "Khortha": "ब्लूबेरी", "Nagpuri": "ब्लूबेरी", "Bhojpuri": "ब्लूबेरी",
        "Bengali": "ব্লুবেরি", "Marathi": "ब्लूबेरी", "Telugu": "బ్లూబెర్రీ", "Tamil": "ப்ளூபெர்ரி", "Gujarati": "બ્લુબેરી", "Punjabi": "ਬਲੂਬੇਰੀ"
    },
    "Cherry": {
        "English": "Cherry", "Hindi": "चेरी", "Khortha": "चेरी", "Nagpuri": "चेरी", "Bhojpuri": "चेरी",
        "Bengali": "চেরি", "Marathi": "चेरी", "Telugu": "చెర్రీ", "Tamil": "செர்ரி", "Gujarati": "ચેરી", "Punjabi": "ਚੈਰੀ"
    },
    "Corn": {
        "English": "Corn (Maize)", "Hindi": "मक्का", "Khortha": "मकई", "Nagpuri": "मकई", "Bhojpuri": "मकई",
        "Bengali": "ভুট্টা", "Marathi": "मका", "Telugu": "మొక్కజొన్న", "Tamil": "மக்காச்சோளம்", "Gujarati": "મકાઈ", "Punjabi": "ਮੱਕੀ"
    },
    "Grape": {
        "English": "Grape", "Hindi": "अंगूर", "Khortha": "अंगूर", "Nagpuri": "अंगूर", "Bhojpuri": "अंगूर",
        "Bengali": "আঙুর", "Marathi": "द्राक्ष", "Telugu": "ద్రాక్ష", "Tamil": "திராட்சை", "Gujarati": "દ્રાક્ષ", "Punjabi": "ਅੰਗੂਰ"
    },
    "Orange": {
        "English": "Orange (Citrus)", "Hindi": "संतरा", "Khortha": "संतरा", "Nagpuri": "संतरा", "Bhojpuri": "संतरा",
        "Bengali": "কমলালেবু", "Marathi": "संत्रा", "Telugu": "నారింజ", "Tamil": "ஆரஞ்சு", "Gujarati": "સંતરા", "Punjabi": "ਸੰਤਰਾ"
    },
    "Peach": {
        "English": "Peach", "Hindi": "आड़ू", "Khortha": "आड़ू", "Nagpuri": "आड़ू", "Bhojpuri": "आड़ू",
        "Bengali": "পিচ", "Marathi": "पीच", "Telugu": "పీచ్", "Tamil": "பீச்", "Gujarati": "પીચ", "Punjabi": "ਆੜੂ"
    },
    "Pepper_bell": {
        "English": "Bell Pepper (Capsicum)", "Hindi": "शिमला मिर्च", "Khortha": "शिमला मिरचाइ", "Nagpuri": "शिमला मिरचा", "Bhojpuri": "शिमला मिरचा",
        "Bengali": "ক্যাপসিকাম", "Marathi": "ढोबळी मिरची", "Telugu": "బెంగళూరు మిరప", "Tamil": "குடைமிளகாய்", "Gujarati": "શિમલા મરચાં", "Punjabi": "ਸ਼ਿਮਲਾ ਮਿਰਚ"
    },
    "Potato": {
        "English": "Potato", "Hindi": "आलू", "Khortha": "आलू", "Nagpuri": "आलू", "Bhojpuri": "आलू",
        "Bengali": "আলু", "Marathi": "बटाटा", "Telugu": "బంగాళాదుంప", "Tamil": "உருளைக்கிழங்கு", "Gujarati": "બટાટા", "Punjabi": "ਆਲੂ"
    },
    "Raspberry": {
        "English": "Raspberry", "Hindi": "रसभरी", "Khortha": "रसभरी", "Nagpuri": "रसभरी", "Bhojpuri": "रसभरी",
        "Bengali": "রাস্পবেরি", "Marathi": "रास्पबेरी", "Telugu": "రాస్ప్బెర్రీ", "Tamil": "ராஸ்பெர்ரி", "Gujarati": "રાસબેરિઝ", "Punjabi": "ਰਸਬੇਰੀ"
    },
    "Soybean": {
        "English": "Soybean", "Hindi": "सोयाबीन", "Khortha": "सोयाबीन", "Nagpuri": "सोयाबीन", "Bhojpuri": "सोयाबीन",
        "Bengali": "সয়াবিন", "Marathi": "सोयाबीन", "Telugu": "సోయాబీన్", "Tamil": "சோயாபீன்", "Gujarati": "સોયાબીન", "Punjabi": "ਸੋਇਆਬੀਨ"
    },
    "Squash": {
        "English": "Squash", "Hindi": "कुम्हड़ा (स्क्वैश)", "Khortha": "कोहड़ा", "Nagpuri": "कोहड़ा", "Bhojpuri": "कोहड़ा",
        "Bengali": "স্কোয়াশ", "Marathi": "भोपळा", "Telugu": "గుమ్మడి", "Tamil": "பூசணி", "Gujarati": "કોળું", "Punjabi": "ਕੱਦੂ"
    },
    "Strawberry": {
        "English": "Strawberry", "Hindi": "स्ट्रॉबेरी", "Khortha": "स्ट्रॉबेरी", "Nagpuri": "स्ट्रॉबेरी", "Bhojpuri": "स्ट्रॉबेरी",
        "Bengali": "স্ট্রবেরি", "Marathi": "स्ट्रॉबेरी", "Telugu": "స్ట్రాబెర్రీ", "Tamil": "ஸ்ட்ராபெரி", "Gujarati": "સ્ટ્રોબેરી", "Punjabi": "ਸਟ੍ਰਾਬੇਰੀ"
    },
    "Tomato": {
        "English": "Tomato", "Hindi": "टमाटर", "Khortha": "टमाटर", "Nagpuri": "बिलाती (टमाटर)", "Bhojpuri": "टमाटर",
        "Bengali": "টমেটো", "Marathi": "टोमॅटो", "Telugu": "టమోటా", "Tamil": "தக்காளி", "Gujarati": "ટમેટા", "Punjabi": "ਟਮਾਟਰ"
    }
}

# Master Disease Translations for All 10 Supported Languages
DISEASE_TRANSLATIONS = {
    "healthy": {
        "English": "Healthy", "Hindi": "स्वस्थ", "Khortha": "बेस/स्वस्थ", "Nagpuri": "स्वस्थ", "Bhojpuri": "स्वस्थ",
        "Bengali": "সুস্থ", "Marathi": "निरोगी", "Telugu": "ఆరోగ్యకరమైనది", "Tamil": "ஆரோக்கியமானது", "Gujarati": "સ્વસ્થ", "Punjabi": "ਤੰਦਰੁਸਤ"
    },
    "Apple_scab": {
        "English": "Apple Scab", "Hindi": "सेब स्कैब (पपड़ी रोग)", "Khortha": "सेब स्कैब बेमारी", "Nagpuri": "सेब स्कैब रोगा", "Bhojpuri": "सेब स्कैब रोग",
        "Bengali": "আপেল স্ক্যাব", "Marathi": "ॲपल स्कॅब", "Telugu": "ఆపిల్ స్కాబ్ తెగులు", "Tamil": "ஆப்பிள் ஸ்கேப் நோய்", "Gujarati": "સફરજન સ્કેબ", "Punjabi": "ਸੇਬ ਸਕੈਬ"
    },
    "Black_rot": {
        "English": "Black Rot", "Hindi": "काला सड़न (ब्लैक रॉट)", "Khortha": "करिया सड़न", "Nagpuri": "करिया सड़न रोगा", "Bhojpuri": "करिया सड़न रोग",
        "Bengali": "কালো পচন রোগ", "Marathi": "काळी कूज", "Telugu": "నల్ల కుళ్లు తెగులు", "Tamil": "கருப்பு அழுகல்", "Gujarati": "કાળો સડો", "Punjabi": "ਕਾਲਾ ਗਲਣਾ"
    },
    "Cedar_apple_rust": {
        "English": "Cedar Apple Rust", "Hindi": "सीडार एप्पल रस्ट (रतुआ)", "Khortha": "लाल रतुआ बेमारी", "Nagpuri": "रतुआ रोगा", "Bhojpuri": "रतुआ रोग",
        "Bengali": "সিডার আপেল মরিচা", "Marathi": "तांबेरा रोग", "Telugu": "సిడార్ ఆపిల్ తుప్పు తెగులు", "Tamil": "சிடார் ஆப்பிள் துரு நோய்", "Gujarati": "સીડર એપલ ગેરુ", "Punjabi": "ਸਿਡਾਰ ਐਪਲ ਰਸਟ"
    },
    "Powdery_mildew": {
        "English": "Powdery Mildew", "Hindi": "चूर्णिल आसिता (पाउडरी मिल्ड्यू)", "Khortha": "सफेद भभुआ बेमारी", "Nagpuri": "सफेद पाऊडर रोगा", "Bhojpuri": "सफेद पाऊडर रोग",
        "Bengali": "পাউডারি মিলডিউ", "Marathi": "भुरी रोग", "Telugu": "బూడిద తెగులు", "Tamil": "சாம்பல் நோய்", "Gujarati": "છારો રોગ", "Punjabi": "ਚੂਰਨਹਾਰ ਉੱਲੀ"
    },
    "Cercospora_leaf_spot": {
        "English": "Cercospora Leaf Spot (Gray Spot)", "Hindi": "सर्कोस्पोरा पत्ती धब्बा रोग", "Khortha": "पत्ता धब्बा बेमारी", "Nagpuri": "पत्ता धब्बा रोगा", "Bhojpuri": "पत्ती धब्बा रोग",
        "Bengali": "সারকোস্পোরা পাতার দাগ", "Marathi": "करकोस्पोरा पानांवरील ठिपके", "Telugu": "సెర్కోస్పోరా ఆకు మచ్చ తెగులు", "Tamil": "செர்கோஸ்போரா இலைப்புள்ளி நோய்", "Gujarati": "સર્કોસ્પોરા પાન ટપકા રોગ", "Punjabi": "ਸਰਕੋਸਪੋਰਾ ਪੱਤਾ ਧੱਬਾ"
    },
    "Common_rust": {
        "English": "Common Rust", "Hindi": "सामान्य रतुआ (कॉमन रस्ट)", "Khortha": "लाल धब्बा बेमारी", "Nagpuri": "रतुआ रोगा", "Bhojpuri": "रतुआ रोग",
        "Bengali": "সাধারণ মরচে রোগ", "Marathi": "तांबेरा रोग", "Telugu": "సాధారణ తుప్పు తెగులు", "Tamil": "பொதுவான துரு நோய்", "Gujarati": "ગેરુ રોગ", "Punjabi": "ਕਾਮਨ ਰਸਟ"
    },
    "Northern_Leaf_Blight": {
        "English": "Northern Leaf Blight", "Hindi": "उत्तरी पत्ती झुलसा", "Khortha": "पत्ता झुलसा बेमारी", "Nagpuri": "पत्ता झुलसा रोगा", "Bhojpuri": "पत्ता झुलसा रोग",
        "Bengali": "নর্দান লিফ ব্লাইট", "Marathi": "पानांवरील करपा", "Telugu": "ఉత్తర ఆకు తెగులు", "Tamil": "வடக்கு இலை கருகல் நோய்", "Gujarati": "પાંદડાનો સુકારો", "Punjabi": "ਨੌਰਦਰਨ ਪੱਤਾ ਝੁਲਸ"
    },
    "Esca_(Black_Measles)": {
        "English": "Esca (Black Measles)", "Hindi": "एस्का (काला चेचक)", "Khortha": "एस्का बेमारी", "Nagpuri": "एस्का रोगा", "Bhojpuri": "एस्का रोग",
        "Bengali": "এসকা (কালো দাগ রোগ)", "Marathi": "एस्का (काळी देवी)", "Telugu": "ఎస్కా (నల్ల మచ్చల తెగులు)", "Tamil": "எஸ்கா (கருப்பு அம்மை)", "Gujarati": "એસ્કા રોગ", "Punjabi": "ਐਸਕਾ ਬਿਮਾਰੀ"
    },
    "Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "English": "Leaf Blight (Isariopsis Spot)", "Hindi": "पत्ती झुलसा (आइसारियोप्सिस)", "Khortha": "पत्ता झुलसा", "Nagpuri": "पत्ता झुलसा रोगा", "Bhojpuri": "पत्ता झुलसा रोग",
        "Bengali": "পাতার ব্লাইট রোগ", "Marathi": "पानांवरील करपा", "Telugu": "ఆకు మచ్చ తెగులు", "Tamil": "இலை கருகல் நோய்", "Gujarati": "પાંદડાનો સુકારો", "Punjabi": "ਪੱਤਾ ਝੁਲਸ ਰੋਗ"
    },
    "Haunglongbing_(Citrus_greening)": {
        "English": "Citrus Greening (Huanglongbing)", "Hindi": "सिट्रस ग्रीनिंग (हौंगलोंगबिंग)", "Khortha": "निम्बू पीला बेमारी", "Nagpuri": "निम्बू पीला रोगा", "Bhojpuri": "निम्बू पीला रोग",
        "Bengali": "সাইট্রাস গ্রিনিং রোগ", "Marathi": "सायट्रस ग्रिनिंग", "Telugu": "సిట్రస్ గ్రీనింగ్ తెగులు", "Tamil": "சிட்ரஸ் கிரீனிங் நோய்", "Gujarati": "સાઇટ્રસ ગ્રીનીંગ", "Punjabi": "ਸਿਟਰਸ ਗ੍ਰੀਨਿੰਗ"
    },
    "Bacterial_spot": {
        "English": "Bacterial Spot", "Hindi": "जीवाणु पत्ती धब्बा (बैक्टीरियल स्पॉट)", "Khortha": "जीवाणु धब्बा बेमारी", "Nagpuri": "जीवाणु धब्बा रोगा", "Bhojpuri": "जीवाणु धब्बा रोग",
        "Bengali": "ব্যাকটেরিয়াল স্পট রোগ", "Marathi": "जिवाणूजन्य ठिपके", "Telugu": "బాక్టీరియల్ మచ్చ తెగులు", "Tamil": "பாக்டீரியா புள்ளி நோய்", "Gujarati": "બેક્ટેરિયલ સ્પોટ", "Punjabi": "ਬੈਕਟੀਰੀਅਲ ਸਪਾਟ"
    },
    "Early_blight": {
        "English": "Early Blight", "Hindi": "अगेता झुलसा (अर्ली ब्लाइट)", "Khortha": "अगिला झुलसा बेमारी", "Nagpuri": "पहिला झुलसा रोगा", "Bhojpuri": "अगिला झुलसा रोग",
        "Bengali": "আগাম ব্লাইট রোগ", "Marathi": "लवकर येणारा करपा", "Telugu": "ముందస్తు తెగులు", "Tamil": "ஆரம்பகால கருகல் நோய்", "Gujarati": "વહેલો સુકારો", "Punjabi": "ਅਰਲੀ ਬਲਾਈਟ"
    },
    "Late_blight": {
        "English": "Late Blight", "Hindi": "पछेता झुलसा (लेट ब्लाइट)", "Khortha": "पाछा झुलसा बेमारी", "Nagpuri": "पाछा झुलसा रोगा", "Bhojpuri": "पाछा झुलसा रोग",
        "Bengali": "নাবি ব্লাইট রোগ", "Marathi": "उशिरा येणारा करपा", "Telugu": "ఆలస్యంగా వచ్చే తెగులు", "Tamil": "தாமதமான கருகல் நோய்", "Gujarati": "મોડો સુકારો", "Punjabi": "ਲੇਟ ਬਲਾਈਟ"
    },
    "Leaf_scorch": {
        "English": "Leaf Scorch", "Hindi": "पत्ती झुलसन (लीफ स्कॉर्च)", "Khortha": "पत्ता झुलसन बेमारी", "Nagpuri": "पत्ता झुलसन रोगा", "Bhojpuri": "पत्ता झुलसन रोग",
        "Bengali": "পাতা পোড়া রোগ", "Marathi": "पान करपणे", "Telugu": "ఆకు మాడు తెగులు", "Tamil": "இலை கருகல் நோய்", "Gujarati": "પાન બળવું", "Punjabi": "ਪੱਤਾ ਝੁਲਸਣਾ"
    },
    "Leaf_Mold": {
        "English": "Leaf Mold", "Hindi": "पत्ती फफूंद (लीफ मोल्ड)", "Khortha": "पत्ता फफूंद बेमारी", "Nagpuri": "पत्ता फफूंद रोगा", "Bhojpuri": "पत्ता फफूंद रोग",
        "Bengali": "পাতার ছত্রাক রোগ", "Marathi": "पानांवरील बुरशी", "Telugu": "ఆకు బూజు తెగులు", "Tamil": "இலை பூஞ்சை நோய்", "Gujarati": "પાન ફૂગ રોગ", "Punjabi": "ਪੱਤਾ ਉੱਲੀ ਰੋਗ"
    },
    "Septoria_leaf_spot": {
        "English": "Septoria Leaf Spot", "Hindi": "सेप्टोरिया पत्ती धब्बा", "Khortha": "सेप्टोरिया धब्बा बेमारी", "Nagpuri": "सेप्टोरिया धब्बा रोगा", "Bhojpuri": "सेप्टोरिया धब्बा रोग",
        "Bengali": "সেপ্টোরিয়া পাতার দাগ", "Marathi": "सेप्टोरिया पानांवरील ठिपके", "Telugu": "సెప్టోరియా ఆకు మచ్చ", "Tamil": "செப்டோரியா இலைப்புள்ளி", "Gujarati": "સેપ્ટોરિયા પાન ટપકા", "Punjabi": "ਸੈਪਟੋਰੀਆ ਪੱਤਾ ਧੱਬਾ"
    },
    "Spider_mites Two-spotted_spider_mite": {
        "English": "Two-Spotted Spider Mite", "Hindi": "दो-धब्बेदार लाल मकड़ी (स्पाइडर माइट)", "Khortha": "लाल मकड़ा बेमारी", "Nagpuri": "लाल मकड़ी रोगा", "Bhojpuri": "लाल मकड़ी कीट",
        "Bengali": "লাল মাকড় পোকা", "Marathi": "दोन ठिपक्यांची लाल कोळी", "Telugu": "రెండు మచ్చల ఎర్ర నల్లి", "Tamil": "இரண்டு புள்ளி சிலந்திப் பூச்சி", "Gujarati": "લાલ મકડી જીવાત", "Punjabi": "ਦੋ ਧੱਬੇਦਾਰ ਮੱਕੜੀ"
    },
    "Target_Spot": {
        "English": "Target Spot", "Hindi": "लक्षित धब्बा रोग (टारगेट स्पॉट)", "Khortha": "गोल धब्बा बेमारी", "Nagpuri": "गोल धब्बा रोगा", "Bhojpuri": "गोल धब्बा रोग",
        "Bengali": "টার্গেট স্পট রোগ", "Marathi": "टार्गेट स्पॉट", "Telugu": "టార్గెట్ స్పాట్ తెగులు", "Tamil": "இலக்கு புள்ளி நோய்", "Gujarati": "ટાર્ગેટ સ્પોટ", "Punjabi": "ਟਾਰਗੇਟ ਸਪਾਟ"
    },
    "Tomato_Yellow_Leaf_Curl_Virus": {
        "English": "Yellow Leaf Curl Virus", "Hindi": "पीली पत्ती मरोड़िया वायरस", "Khortha": "पीला पत्ता मुड़इया बेमारी", "Nagpuri": "पीला पत्ता मुड़इया रोगा", "Bhojpuri": "पीला पत्ती मरोड़ रोग",
        "Bengali": "হলুদ পাতা কোঁকড়ানো ভাইরাস", "Marathi": "पिवळा पानांचा चुरडा-मुरडा", "Telugu": "పసుపు ఆకు ముడత వైరస్", "Tamil": "மஞ்சள் இலை சுருள் வைரஸ்", "Gujarati": "પીળો પર્ણ વલણ વાયરસ", "Punjabi": "ਪੀਲਾ ਪੱਤਾ ਮਰੋੜ ਵਿਸ਼ਾਣੂ"
    },
    "Tomato_mosaic_virus": {
        "English": "Mosaic Virus", "Hindi": "मोज़ेक वायरस", "Khortha": "मोज़ेक बेमारी", "Nagpuri": "मोज़ेक रोगा", "Bhojpuri": "मोज़ेक रोग",
        "Bengali": "মোজাইক ভাইরাস রোগ", "Marathi": "मोज़ॅक व्हायरस", "Telugu": "మొజాయిక్ వైరస్", "Tamil": "மொசைக் வைரஸ் நோய்", "Gujarati": "મોઝેક વાયરસ", "Punjabi": "ਮੋਜ਼ੇਕ ਵਿਸ਼ਾਣੂ"
    }
}

# Healthy Crop Messages in All 10 Supported Languages
HEALTHY_MESSAGES = {
    "English": {
        "organic": "Crop is completely healthy and vigorous. No chemical or organic pesticide required.",
        "chemical": "No chemical treatment needed.",
        "prevention": "Maintain regular drip irrigation, balanced fertilization, and good field sanitation.",
        "voice": "Great news! Your {crop} crop is completely healthy and vigorous. No pesticide or chemical treatment is needed."
    },
    "Hindi": {
        "organic": "फसल पूर्णतः स्वस्थ और सुरक्षित है। किसी कीटनाशक की आवश्यकता नहीं है।",
        "chemical": "किसी रासायनिक उपचार की आवश्यकता नहीं है।",
        "prevention": "नियमित ड्रिप सिंचाई, संतुलित खाद और खेत की स्वच्छता बनाए रखें।",
        "voice": "बधाई हो! आपकी {crop} की फसल पूरी तरह स्वस्थ और सुरक्षित है। किसी भी कीटनाशक या रासायनिक उपचार की आवश्यकता नहीं है।"
    },
    "Khortha": {
        "organic": "फसल पूरा बेस और स्वस्थ है। कोनो कीटनाशक के जरूरत नखे।",
        "chemical": "कोनो दवाई के जरूरत नखे।",
        "prevention": "समय पर पानी और खाद देवे के नियम राखब।",
        "voice": "बधाई हो! तोहर {crop} के फसल एकदम बेस और स्वस्थ है। कोनो दवाई भा कीटनाशक के जरूरत नखे।"
    },
    "Nagpuri": {
        "organic": "फसल पूरा स्वस्थ आहे। कोनो कीटनाशक कर दरकार नखे।",
        "chemical": "कोनो रासायनिक उपचार नखे चाही।",
        "prevention": "खेत कर सफ़ाई और ठीक पानी देवे कर ध्यान राखू।",
        "voice": "बधाई! रउरे कर {crop} कर फसल पूरा स्वस्थ आहे। कोनो कीटनाशक कर दरकार नखे।"
    },
    "Bhojpuri": {
        "organic": "फसल बिल्कुल ठीक आ स्वस्थ बा। कवनो कीटनाशक के जरूरत नइखे।",
        "chemical": "कवनो दवाई के जरूरत नइखे।",
        "prevention": "नियमित सिंचाई आ संतुलित खाद के प्रयोग करीं।",
        "voice": "खुसखबरी! रउआ {crop} के फसल बिल्कुल ठीक आ स्वस्थ बा। कवनो कीटनाशक भा दवाई के जरूरत नइखे।"
    },
    "Bengali": {
        "organic": "ফসল সম্পূর্ণ সুস্থ ও সতেজ। কোনো কীটনাশকের প্রয়োজন নেই।",
        "chemical": "কোনো রাসায়নিক চিকিৎসার প্রয়োজন নেই।",
        "prevention": "সুষম সার ও নিয়মিত জল নিষ্কাশন বজায় রাখুন।",
        "voice": "অভিনন্দন! আপনার {crop} ফসল সম্পূর্ণ সুস্থ। কোনো কীটনাশক বা চিকিৎসার প্রয়োজন নেই।"
    },
    "Marathi": {
        "organic": "पीक पूर्णपणे निरोगी आहे. कोणत्याही कीटकनाशकाची गरज नाही.",
        "chemical": "कोणत्याही रासायनिक उपचारांची गरज नाही.",
        "prevention": "योग्य पाणी व्यवस्थापन आणि संतुलित खते वापरा.",
        "voice": "अभिनंदन! तुमचे {crop} पीक पूर्णपणे निरोगी आहे. कोणत्याही रासायनिक उपचारांची गरज नाही."
    },
    "Telugu": {
        "organic": "పంట పూర్తిగా ఆరోగ్యకరంగా ఉంది. ఎలాంటి పురుగుమందు అవసరం లేదు.",
        "chemical": "ఎలాంటి రసాయన చికిత్స అవసరం లేదు.",
        "prevention": "సరైన నీటి పారుదల మరియు సమతుల్య ఎరువుల యాజమాన్యం పాటించండి.",
        "voice": "అభినందనలు! మీ {crop} పంట పూర్తిగా ఆరోగ్యకరంగా ఉంది. ఎలాంటి పురుగుమందులు అవసరం లేదు."
    },
    "Tamil": {
        "organic": "பயிர் முற்றிலும் ஆரோக்கியமாக உள்ளது. பூச்சிக்கொல்லி தேவையில்லை.",
        "chemical": "எந்த ரசாயன சிகிச்சையும் தேவையில்லை.",
        "prevention": "முறையான பாசனம் மற்றும் சீரான உர நிர்வாகத்தை பராமரிக்கவும்.",
        "voice": "வாழ்த்துகள்! உங்கள் {crop} பயிர் ஆரோக்கியமாக உள்ளது. எந்த பூச்சிக்கொல்லியும் தேவையில்லை."
    },
    "Gujarati": {
        "organic": "પાક સંપૂર્ણપણે સ્વસ્થ છે. કોઈ જંતુનાશકની જરૂર નથી.",
        "chemical": "કોઈ રાસાયણિક સારવારની જરૂર નથી.",
        "prevention": "યોગ્ય પિયત અને સંતુલિત ખાતર વ્યવસ્થાપન જાળવો.",
        "voice": "અભિનંદન! તમારો {crop} પાક સંપૂર્ણ સ્વસ્થ છે. કોઈ જંતુનાશકની જરૂર નથી."
    },
    "Punjabi": {
        "organic": "ਫ਼ਸਲ ਪੂਰੀ ਤਰ੍ਹਾਂ ਤੰਦਰੁਸਤ ਹੈ। ਕਿਸੇ ਕੀਟਨਾਸ਼ਕ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।",
        "chemical": "ਕਿਸੇ ਰਸਾਇਣਕ ਇਲਾਜ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।",
        "prevention": "ਸਹੀ ਸਿੰਚਾਈ ਅਤੇ ਸੰਤੁਲਿਤ ਖਾਦ ਪ੍ਰਬੰਧਨ ਬਣਾਈ ਰੱਖੋ।",
        "voice": "ਵਧਾਈ ਹੋਵੇ! ਤੁਹਾਡੀ {crop} ਦੀ ਫ਼ਸਲ ਪੂਰੀ ਤਰ੍ਹਾਂ ਤੰਦਰੁਸਤ ਹੈ। ਕਿਸੇ ਕੀਟਨਾਸ਼ਕ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।"
    }
}

# Cause & Severity Text by Language
CAUSE_SEVERITY_BY_LANG = {
    "English": {
        "cause_healthy": "None (Plant Vigorous & Healthy)",
        "cause_disease": "Fungal / Bacterial Pathogen",
        "sev_healthy": "None (Healthy)",
        "sev_disease": "Moderate to High"
    },
    "Hindi": {
        "cause_healthy": "कोई नहीं (पौधा पूर्णतः स्वस्थ)",
        "cause_disease": "कवक / जीवाणु रोगज़नक़ (पैथोजन)",
        "sev_healthy": "कोई नहीं (स्वस्थ)",
        "sev_disease": "मध्यम से गंभीर"
    },
    "Khortha": {
        "cause_healthy": "कोनो नखे (पौधा एकदम बेस)",
        "cause_disease": "कवक भा जीवाणु रोगा",
        "sev_healthy": "कोनो नखे (बेस)",
        "sev_disease": "मध्यम से भारी"
    },
    "Nagpuri": {
        "cause_healthy": "कोनो नखे (पौधा पूरा स्वस्थ)",
        "cause_disease": "कवक चाहे जीवाणु रोगा",
        "sev_healthy": "कोनो नखे (स्वस्थ)",
        "sev_disease": "मध्यम से तेज"
    },
    "Bhojpuri": {
        "cause_healthy": "कवनो नइखे (पौधा बिल्कुल ठीक)",
        "cause_disease": "कवक भा जीवाणु रोग",
        "sev_healthy": "कवनो नइखे (स्वस्थ)",
        "sev_disease": "मध्यम से तेज"
    },
    "Bengali": {
        "cause_healthy": "কোনোটি নয় (গাছ সম্পূর্ণ সুস্থ)",
        "cause_disease": "ছত্রাক / ব্যাকটেরিয়া প্যাথোজেন",
        "sev_healthy": "কোনোটি নয় (সুস্থ)",
        "sev_disease": "মাঝারি থেকে তীব্র"
    },
    "Marathi": {
        "cause_healthy": "काहीही नाही (झाड पूर्णपणे निरोगी)",
        "cause_disease": "बुरशीजन्य / जिवाणूजन्य रोगकारक",
        "sev_healthy": "काही नाही (निरोगी)",
        "sev_disease": "मध्यम ते तीव्र"
    },
    "Telugu": {
        "cause_healthy": "ఏదీ లేదు (మొక్క పూర్తిగా ఆరోగ్యకరం)",
        "cause_disease": "శిలీంధ్ర / బ్యాక్టీరియా తెగులు కారకం",
        "sev_healthy": "ఏదీ లేదు (ఆరోగ్యకరం)",
        "sev_disease": "మధ్యస్థం నుండి తీవ్రం"
    },
    "Tamil": {
        "cause_healthy": "எதுவுமில்லை (பயிர் முழு ஆரோக்கியம்)",
        "cause_disease": "பூஞ்சை / பாக்டீரியா நோய்க்கிருமி",
        "sev_healthy": "எதுவுமில்லை (ஆரோக்கியம்)",
        "sev_disease": "மிதமானது முதல் தீவிரமானது"
    },
    "Gujarati": {
        "cause_healthy": "કોઈ નહીં (છોડ સંપૂર્ણ સ્વસ્થ)",
        "cause_disease": "ફૂગ / બેક્ટેરિયા પેથોજેન",
        "sev_healthy": "કોઈ નહીં (સ્વસ્થ)",
        "sev_disease": "મધ્યમથી વધુ"
    },
    "Punjabi": {
        "cause_healthy": "ਕੋਈ ਨਹੀਂ (ਪੌਦਾ ਪੂਰੀ ਤਰ੍ਹਾਂ ਤੰਦਰੁਸਤ)",
        "cause_disease": "ਉੱਲੀ / ਜੀਵਾਣੂ ਰੋਗਕਾਰੀ",
        "sev_healthy": "ਕੋਈ ਨਹੀਂ (ਤੰਦਰੁਸਤ)",
        "sev_disease": "ਦਰਮਿਆਨਾ ਤੋਂ ਉੱਚਾ"
    }
}


def translate_crop(raw_crop: str, target_lang: str = "Hindi") -> str:
    """Translates crop name into the selected language."""
    clean = raw_crop.replace(" ", "_").strip()
    for key, trans in CROP_TRANSLATIONS.items():
        if key.lower() == clean.lower() or key.lower() in clean.lower():
            return trans.get(target_lang) or trans.get("English", raw_crop)
    return raw_crop


def translate_disease(raw_disease: str, target_lang: str = "Hindi") -> str:
    """Translates disease name into the selected language."""
    clean = raw_disease.replace(" ", "_").strip().lower()
    if "healthy" in clean:
        return DISEASE_TRANSLATIONS["healthy"].get(target_lang) or "Healthy"
    for key, trans in DISEASE_TRANSLATIONS.items():
        key_clean = key.replace(" ", "_").strip().lower()
        if key_clean == clean or key_clean in clean or clean in key_clean:
            return trans.get(target_lang) or trans.get("English", raw_disease)
    if target_lang == "English":
        return raw_disease.replace("_", " ")
    return raw_disease.replace("_", " ")


def translate_disease_class(disease_class: str, target_lang: str = "Hindi") -> tuple[str, str, str]:
    """
    Parses Crop___Disease into (crop, disease, display_title) in the selected language.
    """
    parts = disease_class.split("___") if "___" in disease_class else [disease_class, "Condition"]
    raw_crop = parts[0]
    raw_disease = parts[1] if len(parts) > 1 else "healthy"

    crop_disp = translate_crop(raw_crop, target_lang)
    disease_disp = translate_disease(raw_disease, target_lang)
    display_title = f"{crop_disp} - {disease_disp}"
    return crop_disp, disease_disp, display_title


# Detailed Multilingual Treatment Repository
MULTILINGUAL_DICTIONARY = {
    "Potato___Late_blight": {
        "crop": {"Hindi": "आलू", "English": "Potato"},
        "disease": {"Hindi": "पछेता झुलसा (लेट ब्लाइट)", "English": "Late Blight"},
        "organic": {
            "Hindi": "5% नीम के बीज के अर्क (NSKE) या ट्राइकोडरमा हरज़ियानम (5 ग्राम/लीटर) का छिड़काव करें। संक्रमित पत्तियों को तुरंत नष्ट करें।",
            "Khortha": "5% नीम तेल चाहे ट्राइकोडरमा (5 ग्राम/लीटर) के पानी में मिलाय के छिड़काव करा। खराब पात के तुरंत फेंक देब।",
            "Nagpuri": "5% नीम कर तेल चाहे ट्राइकोडरमा कर पानी में छिड़काव करू। बीमारी वाला पात के उखाड़ के फेंक देबू।",
            "Bhojpuri": "5% नीम के तेल भा ट्राइकोडरमा (5 ग्राम/लीटर) छिड़कीं। सड़ा भईल पतोई तुरंत खेत से बाहर करीं।",
            "Bengali": "৫% নিম বীজের নির্যাস বা ট্রাইকোডার্মা (৫ গ্রাম/লিটার) স্প্রে করুন। আক্রান্ত পাতা ধ্বংস করুন।",
            "Marathi": "५% कडुनिंब अर्काची किंवा ट्रायकोडेर्माची (५ ग्रॅम/लीटर) फवारणी करा. बाधित पाने नष्ट करा.",
            "Telugu": "5% వేప గింజల కషాయం లేదా ట్రైకోడెర్మా (5 గ్రా/లీ) పిచికారీ చేయండి. సోకిన ఆకులను తొలగించండి.",
            "Tamil": "5% வேப்ப எண்ணெய் அல்லது ட்ரைக்கோடெர்மா (5 கிராம்/லிட்டர்) தெளிக்கவும். பாதிக்கப்பட்ட இலைகளை அழிக்கவும்.",
            "Gujarati": "5% લીમડાના તેલ અથવા ટ્રાઇકોડર્મા (5 ગ્રામ/લીટર) નો છંટકાવ કરો. ચેપગ્રસ્ત પાંદડા નાશ કરો.",
            "Punjabi": "5% ਨੀਮ ਦੇ ਅਰਕ ਜਾਂ ਟ੍ਰਾਈਕੋਡਰਮਾ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਛਿੜਕਾਅ ਕਰੋ। ਬਿਮਾਰ ਪੱਤਿਆਂ ਨੂੰ ਨਸ਼ਟ ਕਰੋ।",
            "English": "Spray 5% Neem Seed Kernel Extract (NSKE) or Trichoderma harzianum @ 5 g/L. Remove and destroy infected lower leaves immediately."
        },
        "chemical": {
            "Hindi": "साइमोक्सानिल 8% + मैंकोज़ेब 64% WP @ 2.5 ग्राम/लीटर या डाइमेथोमॉर्फ 50% WP @ 1.0 ग्राम/लीटर का छिड़काव करें।",
            "English": "Spray Cymoxanil 8% + Mancozeb 64% WP @ 2.5 g/L or Dimethomorph 50% WP @ 1.0 g/L at 7-10 day intervals."
        },
        "prevention": {
            "Hindi": "फसल चक्र अपनाएं, ड्रिप सिंचाई का प्रयोग करें और पत्तियों पर पानी ठहरने न दें।",
            "English": "Practice crop rotation, maintain 15-20 cm earthing-up, and avoid overhead sprinkler irrigation."
        }
    },
    "Tomato___Early_blight": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "अगेता झुलसा (अर्ली ब्लाइट)", "English": "Early Blight"},
        "organic": {
            "Hindi": "सूडोमोनास फ्लोरोसेंस 1% WP @ 5 ग्राम/लीटर और 5% नीम तेल का छिड़काव करें। निचली 30 सेमी पत्तियों की छंटाई करें।",
            "Khortha": "नीम तेल और सूडोमोनास (5 ग्राम/लीटर) के छिड़काव करा। नीचा के सड़ा पात छांट देब।",
            "Nagpuri": "नीम तेल और सूडोमोनास कर पानी में घोल बनाय के छिड़काव करू।",
            "Bhojpuri": "नीम के तेल 5% आ सूडोमोनास (5 ग्राम/लीटर) छिड़कीं। निचला पतोई छंटाई करीं।",
            "Bengali": "সিউডোমোনাস (৫ গ্রাম/লিটার) ও নিম তেল স্প্রে করুন। নীচের আক্রান্ত পাতা ছেঁটে দিন।",
            "Marathi": "सुडोमोनास (५ ग्रॅम/लीटर) आणि कडुनिंब तेलाची फवारणी करा. खालची पाने छाटा.",
            "Telugu": "స్యూడోమోనాస్ (5 గ్రా/లీ) మరియు వేప నూనె పిచికారీ చేయండి. క్రింది ఆకులను కత్తిరించండి.",
            "Tamil": "சூடோமோனாஸ் (5 கிராம்/லிட்டர்) மற்றும் வேப்ப எண்ணெய் தெளிக்கவும்.",
            "Gujarati": "સ્યુડોમોનાસ (5 ગ્રામ/લીટર) અને લીમડાના તેલનો છંટકાવ કરો.",
            "Punjabi": "ਸੂਡੋਮੋਨਾਸ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਅਤੇ ਨੀਮ ਦੇ ਤੇਲ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Apply Pseudomonas fluorescens 1% WP @ 5 g/L combined with 5% Neem oil. Prune lower 30 cm foliage to prevent soil-splash."
        },
        "chemical": {
            "Hindi": "डाइफेनोकोनाज़ोल 25% EC @ 0.5 मिली/लीटर या एजोक्सीस्ट्रोबिन 18.2% + डाइफेनोकोनाज़ोल 11.4% SC @ 1.0 मिली/लीटर छिड़कें।",
            "English": "Spray Difenoconazole 25% EC @ 0.5 ml/L or Azoxystrobin + Difenoconazole SC @ 1.0 ml/L at initial symptom appearance."
        },
        "prevention": {
            "Hindi": "मल्चिंग का प्रयोग करें, 60 सेमी पंक्ति दूरी रखें और ड्रिप सिंचाई अपनाएं।",
            "English": "Use silver-black polyethylene mulch, maintain 60 cm row spacing, and drip irrigate."
        }
    },
    "Corn___Common_rust": {
        "crop": {"Hindi": "मक्का", "English": "Corn (Maize)"},
        "disease": {"Hindi": "सामान्य रतुआ (कॉमन रस्ट)", "English": "Common Rust"},
        "organic": {
            "Hindi": "5% नीम के बीज के अर्क या खट्टी छाछ (1:10 घोल) का छिड़काव करें। प्रतिरोधक किस्म (PMH-1, HQPM-1) बोएं।",
            "Khortha": "नीम तेल चाहे घोरल मही (छाछ) के छिड़काव करा। उन्नत बीहन लगावा।",
            "Nagpuri": "नीम कर तेल चाहे मही कर घोल पानी में मिलाय के छिड़काव करू।",
            "Bhojpuri": "नीम के तेल भा खट्टा मट्ठा (छाछ) छिड़कीं। बढ़िया बीज बोईं।",
            "Bengali": "৫% নিম তেল বা ঘোল (১:১০ অনুপাত) স্প্রে করুন। প্রতিরোধী জাত ব্যবহার করুন।",
            "Marathi": "५% कडुनिंब तेल किंवा आंबट ताक (१:१०) फवारा. तांबेरा-रोधक वाण लावा.",
            "Telugu": "5% వేప నూనె లేదా మజ్జిగ ద్రావణం పిచికారీ చేయండి. నిరోధక రకాలను వాడండి.",
            "Tamil": "5% வேப்ப எண்ணெய் தெளிக்கவும். நோய் எதிர்ப்பு ரகங்களை பயிரிடவும்.",
            "Gujarati": "5% લીમડાનું તેલ અથવા ખાટી છાશનો છંટકાવ કરો. પ્રતિકારક જાતો વાવો.",
            "Punjabi": "5% ਨੀਮ ਦਾ ਤੇਲ ਜਾਂ ਖੱਟੀ ਲੱਸੀ ਦਾ ਛਿੜਕਾਅ ਕਰੋ। ਉੱਨਤ ਬੀਜ ਬੀਜੋ।",
            "English": "Spray 5% Neem Seed Kernel Extract or fermented buttermilk (1:10 dilution). Plant resistant maize hybrids like PMH-1 or HQPM-1."
        },
        "chemical": {
            "Hindi": "मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर या एजोक्सीस्ट्रोबिन 23% SC @ 1.0 मिली/लीटर का छिड़काव करें।",
            "English": "Apply Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin 23% SC @ 1.0 ml/L at first pustule appearance."
        },
        "prevention": {
            "Hindi": "60 x 20 सेमी दूरी रखें और संतुलित एनपीके (120:60:40) उर्वरक दें।",
            "English": "Maintain 60 x 20 cm spacing and apply balanced NPK (120:60:40 kg/ha)."
        }
    },
    "Apple___Apple_scab": {
        "crop": {"Hindi": "सेब", "English": "Apple"},
        "disease": {"Hindi": "सेब स्कैब", "English": "Apple Scab"},
        "organic": {"Hindi": "कॉपर आधारित जैविक कवकनाशी या 5% नीम तेल का छिड़काव करें।", "English": "Apply copper-based organic spray or 5% Neem Seed Kernel Extract."},
        "chemical": {"Hindi": "मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर या डिफेनोकोनाज़ोल 25% EC छिड़कें।", "English": "Apply Mancozeb 75% WP @ 2.5 g/L or Difenoconazole 25% EC @ 0.5 ml/L."},
        "prevention": {"Hindi": "उचित जल निकासी रखें, गिरे पत्तों को एकत्र कर नष्ट करें।", "English": "Maintain proper drainage and destroy infected fallen leaves."}
    },
    "Apple___Black_rot": {
        "crop": {"Hindi": "सेब", "English": "Apple"},
        "disease": {"Hindi": "ब्लैक रॉट (काला सड़न)", "English": "Black Rot"},
        "organic": {"Hindi": "5% नीम तेल और ट्राइकोडरमा का छिड़काव करें।", "English": "Spray 5% neem oil and apply Trichoderma bio-agent."},
        "chemical": {"Hindi": "थियोफेनेट मिथाइल 70% WP @ 1.0 ग्राम/लीटर का छिड़काव करें।", "English": "Apply Thiophanate methyl 70% WP @ 1.0 g/L or Captan 50% WP @ 2.5 g/L."},
        "prevention": {"Hindi": "संक्रमित टहनियों और सड़े फलों को तुरंत काटकर हटाएं।", "English": "Prune infected cankers and promptly bury mummified fruit."}
    },
    "Apple___Cedar_apple_rust": {
        "crop": {"Hindi": "सेब", "English": "Apple"},
        "disease": {"Hindi": "सीडार एप्पल रस्ट (रतुआ)", "English": "Cedar Apple Rust"},
        "organic": {"Hindi": "सल्फर आधारित कवकनाशी या बेकिंग सोडा (5 ग्राम/लीटर) का छिड़काव करें।", "English": "Spray wettable sulfur @ 3 g/L or sodium bicarbonate solution."},
        "chemical": {"Hindi": "मायक्लोब्यूटानिल 10% WP या प्रोपिकोनाज़ोल 25% EC का छिड़काव करें।", "English": "Apply Myclobutanil 10% WP or Propiconazole 25% EC @ 1 ml/L."},
        "prevention": {"Hindi": "प्रतिरोधक किस्में लगाएं और पास के जंगलों से जुनिपर हटाएँ।", "English": "Plant resistant cultivars and remove nearby juniper hosts."}
    },
    "Grape___Black_rot": {
        "crop": {"Hindi": "अंगूर", "English": "Grape"},
        "disease": {"Hindi": "ब्लैक रॉट (काला सड़न)", "English": "Black Rot"},
        "organic": {"Hindi": "बोर्डो मिश्रण 1% या कॉपर ऑक्सीक्लोराइड 50% WP @ 3 ग्राम/लीटर छिड़कें।", "English": "Apply 1% Bordeaux mixture or Copper Oxychloride 50% WP @ 3.0 g/L."},
        "chemical": {"Hindi": "डाइफेनोकोनाज़ोल 25% EC @ 0.5 मिली/लीटर या मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर छिड़कें।", "English": "Apply Difenoconazole 25% EC @ 0.5 ml/L or Mancozeb 75% WP @ 2.5 g/L."},
        "prevention": {"Hindi": "बेलों की उचित छंटाई करें ताकि धूप और हवा का संचार बना रहे।", "English": "Prune grape canopy to ensure direct sunlight and rapid leaf drying."}
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": {"Hindi": "अंगूर", "English": "Grape"},
        "disease": {"Hindi": "एस्का (काला चेचक)", "English": "Esca (Black Measles)"},
        "organic": {"Hindi": "कटाई के घावों पर ट्राइकोडरमा पेस्ट लगाएं।", "English": "Apply Trichoderma paste on pruning wounds immediately."},
        "chemical": {"Hindi": "घाव सीलेंट (बेनोमिल या कॉपर पेस्ट) का उपयोग करें।", "English": "Seal thick pruning cuts with fungicidal wound sealant."},
        "prevention": {"Hindi": "सूखे मौसम में ही छंटाई करें ताकि फफूंद के बीजाणु न घुसें।", "English": "Prune only in dry weather and disinfect shears between vines."}
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": {"Hindi": "अंगूर", "English": "Grape"},
        "disease": {"Hindi": "पत्ती झुलसा", "English": "Leaf Blight"},
        "organic": {"Hindi": "5% नीम के अर्क और स्यूडोमोनास का छिड़काव करें।", "English": "Apply 5% neem extract and Pseudomonas fluorescens."},
        "chemical": {"Hindi": "कार्बेन्डाजिम 50% WP @ 1.0 ग्राम/लीटर का छिड़काव करें।", "English": "Spray Carbendazim 50% WP @ 1.0 g/L at early infection stage."},
        "prevention": {"Hindi": "नीचे की संक्रमित पत्तियां हटाएं और खेत साफ रखें।", "English": "Remove lower infected foliage and avoid sprinkler irrigation."}
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": {"Hindi": "संतरा", "English": "Orange (Citrus)"},
        "disease": {"Hindi": "सिट्रस ग्रीनिंग (हौंगलोंगबिंग)", "English": "Citrus Greening"},
        "organic": {"Hindi": "नीम तेल 2% छिड़ककर सिट्रस साइला कीट को नियंत्रित करें।", "English": "Spray 2% neem oil and introduce parasitic wasps (Tamarixia radiata)."},
        "chemical": {"Hindi": "इमिडाक्लोप्रिड 17.8% SL @ 0.5 मिली/लीटर कीट वेक्टर के नियंत्रण के लिए छिड़कें।", "English": "Spray Imidacloprid 17.8% SL @ 0.5 ml/L to suppress psyllid insect vectors."},
        "prevention": {"Hindi": "प्रमाणित रोगमुक्त नर्सरी पौधों का ही रोपण करें।", "English": "Plant only certified disease-free grafted saplings."}
    },
    "Peach___Bacterial_spot": {
        "crop": {"Hindi": "आड़ू", "English": "Peach"},
        "disease": {"Hindi": "जीवाणु पत्ती धब्बा", "English": "Bacterial Spot"},
        "organic": {"Hindi": "कॉपर सल्फेट आधारित जैविक स्प्रे करें।", "English": "Apply copper sulfate organic spray at dormant bud swell."},
        "chemical": {"Hindi": "स्ट्रेप्टोसाइक्लिन @ 0.5 ग्राम/10 लीटर + कॉपर ऑक्सीक्लोराइड छिड़कें।", "English": "Spray Streptocycline @ 0.5 g/10L combined with Copper Oxychloride."},
        "prevention": {"Hindi": "हवा के रुख में सुरक्षात्मक पेड़ लगाएं और छंटाई नियंत्रित रखें।", "English": "Plant windbreaks and prune tree canopy to accelerate drying."}
    },
    "Pepper_bell___Bacterial_spot": {
        "crop": {"Hindi": "शिमला मिर्च", "English": "Bell Pepper"},
        "disease": {"Hindi": "जीवाणु धब्बा रोग", "English": "Bacterial Spot"},
        "organic": {"Hindi": "स्यूडोमोनास फ्लोरोसेंस @ 5 ग्राम/लीटर और नीम तेल छिड़कें।", "English": "Apply Pseudomonas fluorescens @ 5 g/L with 5% neem extract."},
        "chemical": {"Hindi": "कॉपर हाइड्रोक्साइड 77% WP @ 2.0 ग्राम/लीटर छिड़कें।", "English": "Spray Copper Hydroxide 77% WP @ 2.0 g/L or Streptocycline @ 1 g/10L."},
        "prevention": {"Hindi": "गर्म पानी (50°C पर 25 मिनट) से बीजोपचार करें।", "English": "Hot water seed treatment at 50°C for 25 minutes before sowing."}
    },
    "Tomato___Bacterial_spot": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "बैक्टीरियल स्पॉट", "English": "Bacterial Spot"},
        "organic": {"Hindi": "नीम तेल 5% और ट्राइकोडर्मा का छिड़काव करें।", "English": "Spray 5% neem seed extract and Trichoderma viride."},
        "chemical": {"Hindi": "कॉपर ऑक्सीक्लोराइड 50% WP @ 2.5 ग्राम/लीटर + स्ट्रेप्टोसाइक्लिन 1 ग्राम/10 लीटर।", "English": "Apply Copper Oxychloride 50% WP @ 2.5 g/L + Streptocycline 1 g/10L."},
        "prevention": {"Hindi": "पौधों पर ऊपर से पानी छिड़कने से बचें और फसल चक्र अपनाएं।", "English": "Avoid overhead sprinkling and maintain a 2-year non-solanaceous rotation."}
    },
    "Tomato___Leaf_Mold": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "लीफ मोल्ड (पत्ती फफूंद)", "English": "Leaf Mold"},
        "organic": {"Hindi": "बेकिंग सोडा (5 ग्राम/लीटर) या स्यूडोमोनास का छिड़काव करें।", "English": "Spray baking soda solution (5 g/L) or Pseudomonas fluorescens."},
        "chemical": {"Hindi": "डाइफेनोकोनाज़ोल 25% EC @ 0.5 मिली/लीटर छिड़कें।", "English": "Apply Difenoconazole 25% EC @ 0.5 ml/L or Chlorothalonil 75% WP @ 2 g/L."},
        "prevention": {"Hindi": "पॉलीहाउस में वेंटिलेशन बढ़ाएं और आर्द्रता 85% से नीचे रखें।", "English": "Increase greenhouse ventilation to maintain relative humidity below 85%."}
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "सेप्टोरिया लीफ स्पॉट", "English": "Septoria Leaf Spot"},
        "organic": {"Hindi": "5% नीम तेल स्प्रे करें और निचली 30 सेमी पत्तियां छांटें।", "English": "Spray 5% neem extract and prune lower 30 cm foliage to stop soil-splash."},
        "chemical": {"Hindi": "मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर या क्लोरोथैलोनिल 75% WP @ 2 ग्राम/लीटर।", "English": "Apply Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2.0 g/L."},
        "prevention": {"Hindi": "प्लास्टिक मल्चिंग अपनाएं और ड्रिप सिंचाई का प्रयोग करें।", "English": "Use silver-black plastic mulch and adopt drip irrigation."}
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "दो-धब्बेदार लाल मकड़ी (स्पाइडर माइट)", "English": "Two-Spotted Spider Mite"},
        "organic": {"Hindi": "नीम तेल 5% या वर्मीवाश (1:5 घोल) का पत्तियों के नीचे छिड़काव करें।", "English": "Spray 5% neem oil or wettable sulfur @ 3 g/L directly under leaf undersides."},
        "chemical": {"Hindi": "फेनपायरोक्सीमेट 5% EC @ 1.0 मिली/लीटर या प्रोपारगाइट 57% EC @ 2.0 मिली/लीटर छिड़कें।", "English": "Apply Fenpyroximate 5% EC @ 1.0 ml/L or Propargite 57% EC @ 2.0 ml/L."},
        "prevention": {"Hindi": "धूल-मिट्टी कम रखें और प्रीडेटरी माइट्स को बढ़ावा दें।", "English": "Keep field borders wet to reduce dust and conserve predatory mites."}
    },
    "Tomato___Target_Spot": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "टारगेट स्पॉट (लक्षित धब्बा रोग)", "English": "Target Spot"},
        "organic": {"Hindi": "ट्राइकोडर्मा हरज़ियानम @ 5 ग्राम/लीटर और नीम तेल का छिड़काव करें।", "English": "Apply Trichoderma harzianum @ 5 g/L with 5% neem extract."},
        "chemical": {"Hindi": "एजोक्सीस्ट्रोबिन 23% SC @ 1.0 मिली/लीटर छिड़कें।", "English": "Apply Azoxystrobin 23% SC @ 1.0 ml/L or Difenoconazole 25% EC."},
        "prevention": {"Hindi": "पौधों के बीच पर्याप्त दूरी रखें ताकि हवा का संचार बना रहे।", "English": "Maintain 60 cm row spacing to optimize sunlight penetration and airflow."}
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "पीली पत्ती मरोड़िया वायरस", "English": "Tomato Yellow Leaf Curl Virus"},
        "organic": {"Hindi": "पीले चिपचिपे ट्रैप (12/एकड़) लगाएं और 5% नीम तेल छिड़कें।", "English": "Install yellow sticky traps (12 traps/acre) and spray 5% neem oil for whitefly control."},
        "chemical": {"Hindi": "सफेद मक्खी नियंत्रण के लिए एसिटामिप्रिड 20% SP @ 0.5 ग्राम/लीटर छिड़कें।", "English": "Spray Acetamiprid 20% SP @ 0.5 g/L or Thiamethoxam 25% WG @ 0.3 g/L."},
        "prevention": {"Hindi": "वायरस प्रतिरोधी संकर (जैसे US-3140, साहो) का चयन करें।", "English": "Plant certified TYLCV-resistant hybrid seeds and use 40-mesh insect net in nursery."}
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "टमाटर मोज़ेक वायरस", "English": "Tomato Mosaic Virus"},
        "organic": {"Hindi": "संक्रमित पौधों को तुरंत उखाड़कर नष्ट करें। बीज को ट्राइसोडियम फॉस्फेट से शोधित करें।", "English": "Rogue out infected plants. Treat seed in 10% Trisodium phosphate for 15 min."},
        "chemical": {"Hindi": "वायरस पर रासायनिक कवकनाशी काम नहीं करते। रोगवाहक कीटों का नियंत्रण करें।", "English": "Chemical fungicides are ineffective against viruses. Disinfect tools with 10% bleach."},
        "prevention": {"Hindi": "खेत में काम करते समय धूम्रपान न करें और हाथ साबुन से धोएं।", "English": "Prohibit smoking in fields and wash hands with soap before handling tomato plants."}
    },
    "Cherry___Powdery_mildew": {
        "crop": {"Hindi": "चेरी", "English": "Cherry"},
        "disease": {"Hindi": "चूर्णिल आसिता (पाउडरी मिल्ड्यू)", "English": "Powdery Mildew"},
        "organic": {
            "Hindi": "5% नीम तेल या घुलनशील गंधक (सल्फर 80% WP @ 2.5 ग्राम/लीटर) का छिड़काव करें। बेकिंग सोडा का 0.5% घोल भी प्रभावी है।",
            "Khortha": "5% नीम तेल चाहे घुलनशील गंधक के पानी में मिलाय के छिड़काव करा।",
            "Nagpuri": "5% नीम कर तेल चाहे सल्फर कर घोल बनाय के छिड़काव करू।",
            "Bhojpuri": "5% नीम के तेल भा सल्फर (गंधक) के छिड़काव करीं।",
            "Bengali": "৫% নিম তেল বা দ্রবণীয় সালফার (২.৫ গ্রাম/লিটার) স্প্রে করুন।",
            "Marathi": "५% कडुनिंब तेल किंवा विद्राव्य गंधक (२.५ ग्रॅम/लीटर) फवारा.",
            "Telugu": "5% వేప నూనె లేదా సల్ఫర్ (2.5 గ్రా/లీ) పిచికారీ చేయండి.",
            "Tamil": "5% வேப்ப எண்ணெய் அல்லது கந்தகம் (2.5 கிராம்/லிட்டர்) தெளிக்கவும்.",
            "Gujarati": "5% લીમડાનું તેલ અથવા સલ્ફર (2.5 ગ્રામ/લીટર) નો છંટકાવ કરો.",
            "Punjabi": "5% ਨੀਮ ਦਾ ਤੇਲ ਜਾਂ ਘੁਲਣਸ਼ੀਲ ਗੰਧਕ (2.5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Spray 5% neem oil or wettable sulfur 80% WP @ 2.5 g/L. Potassium bicarbonate (5 g/L) is also an effective bio-control."
        },
        "chemical": {
            "Hindi": "मायक्लोब्यूटानिल 10% WP @ 1 ग्राम/लीटर या हेक्साकोनाज़ोल 5% SC @ 1 मिली/लीटर का छिड़काव करें।",
            "English": "Spray Myclobutanil 10% WP @ 1.0 g/L or Hexaconazole 5% SC @ 1.0 ml/L at early symptom development."
        },
        "prevention": {
            "Hindi": "संक्रमित टहनियों को छांटें, पेड़ों के बीच पर्याप्त वायु संचार रखें और अधिक नाइट्रोजन खाद से बचें।",
            "English": "Prune infected shoots, ensure adequate tree canopy airflow, and avoid excessive nitrogen fertilization."
        }
    },
    "Corn___Cercospora_leaf_spot": {
        "crop": {"Hindi": "मक्का", "English": "Corn (Maize)"},
        "disease": {"Hindi": "सर्कोस्पोरा पत्ती धब्बा रोग", "English": "Cercospora Leaf Spot"},
        "organic": {
            "Hindi": "5% नीम के बीज के अर्क (NSKE) या ट्राइकोडरमा हरज़ियानम (5 ग्राम/लीटर) का छिड़काव करें। फसल अवशेष नष्ट करें।",
            "Khortha": "5% नीम के बीज के अर्क चाहे ट्राइकोडरमा के छिड़काव करा।",
            "Nagpuri": "5% नीम कर अर्क चाहे ट्राइकोडरमा कर छिड़काव करू।",
            "Bhojpuri": "5% नीम के अर्क भा ट्राइकोडरमा (5 ग्राम/लीटर) छिड़कीं।",
            "Bengali": "৫% নিম বীজের নির্যাস বা ট্রাইকোডার্মা (৫ গ্রাম/লিটার) স্প্রে করুন।",
            "Marathi": "५% कडुनिंब अर्क किंवा ट्रायकोडेर्मा (५ ग्रॅम/लीटर) फवारा.",
            "Telugu": "5% వేప గింజల కషాయం లేదా ట్రైకోడెర్మా (5 గ్రా/లీ) పిచికారీ చేయండి.",
            "Tamil": "5% வேப்ப எண்ணெய் அல்லது ட்ரைக்கோடெர்மா தெளிக்கவும்.",
            "Gujarati": "5% લીમડાના અર્ક અથવા ટ્રાઇકોડર્મા (5 ગ્રામ/લીટર) નો છંટકાવ કરો.",
            "Punjabi": "5% ਨੀਮ ਦੇ ਅਰਕ ਜਾਂ ਟ੍ਰਾਈਕੋਡਰਮਾ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Spray 5% Neem Seed Kernel Extract (NSKE) or Trichoderma harzianum @ 5 g/L. Destroy infected plant debris."
        },
        "chemical": {
            "Hindi": "एज़ोक्सीस्ट्रोबिन 18.2% + डाइफेनोकोनाज़ोल 11.4% SC @ 1.0 मिली/लीटर या मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर छिड़कें।",
            "English": "Apply Azoxystrobin + Difenoconazole SC @ 1.0 ml/L or Mancozeb 75% WP @ 2.5 g/L at early symptom onset."
        },
        "prevention": {
            "Hindi": "फसल चक्र अपनाएं (दलहनी फसलों के साथ), 60 x 20 सेमी की दूरी रखें और गहरी जुताई करें।",
            "English": "Practice 2-year crop rotation with legumes, maintain 60 x 20 cm spacing, and deep-plough infected stubble."
        }
    },
    "Corn___Northern_Leaf_Blight": {
        "crop": {"Hindi": "मक्का", "English": "Corn (Maize)"},
        "disease": {"Hindi": "उत्तरी पत्ती झुलसा", "English": "Northern Leaf Blight"},
        "organic": {
            "Hindi": "खट्टी छाछ (1:10 अनुपात) या 5% नीम तेल और स्यूडोमोनास फ्लोरोसेंस (5 ग्राम/लीटर) का छिड़काव करें।",
            "Khortha": "घोरल मही (छाछ) चाहे 5% नीम तेल के घोल छिड़काव करा।",
            "Nagpuri": "मही कर घोल चाहे 5% नीम तेल कर छिड़काव करू।",
            "Bhojpuri": "खट्टा मट्ठा (छाछ) भा 5% नीम के तेल के छिड़काव करीं।",
            "Bengali": "ঘোল (১:১০ অনুপাত) বা ৫% নিম তেল স্প্রে করুন।",
            "Marathi": "आंबट ताक (१:१०) किंवा ५% कडुनिंब तेलाची फवारणी करा.",
            "Telugu": "మజ్జిగ ద్రావణం లేదా 5% వేప నూనె పిచికారీ చేయండి.",
            "Tamil": "மோர் கரைசல் அல்லது 5% வேப்ப எண்ணெய் தெளிக்கவும்.",
            "Gujarati": "ખાટી છાશ અથવા 5% લીમડાના તેલનો છંટકાવ કરો.",
            "Punjabi": "ਖੱਟੀ ਲੱਸੀ ਜਾਂ 5% ਨੀਮ ਦਾ ਤੇਲ ਛਿੜਕੋ।",
            "English": "Spray fermented buttermilk (1:10 dilution) or 5% neem oil with Pseudomonas fluorescens @ 5 g/L."
        },
        "chemical": {
            "Hindi": "प्रोपिकोनाज़ोल 25% EC @ 1.0 मिली/लीटर या मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर का छिड़काव करें।",
            "English": "Apply Propiconazole 25% EC @ 1.0 ml/L or Mancozeb 75% WP @ 2.5 g/L at knee-high stage."
        },
        "prevention": {
            "Hindi": "प्रतिरोधक संकर किस्में (जैसे PMH-1) बोएं, बीज शोधन करें और कटाई के बाद खेत की गहरी जुताई करें।",
            "English": "Sow resistant hybrids (e.g. PMH-1), perform seed treatment with Thiram @ 3 g/kg, and deep-plough residue."
        }
    },
    "Potato___Early_blight": {
        "crop": {"Hindi": "आलू", "English": "Potato"},
        "disease": {"Hindi": "अगेता झुलसा (अर्ली ब्लाइट)", "English": "Early Blight"},
        "organic": {
            "Hindi": "ट्राइकोडरमा हरज़ियानम (5 ग्राम/लीटर) और 5% नीम के बीज के अर्क (NSKE) का पत्तियों पर छिड़काव करें।",
            "Khortha": "ट्राइकोडरमा (5 ग्राम/लीटर) और 5% नीम तेल के पानी में मिलाय के छिड़काव करा।",
            "Nagpuri": "ट्राइकोडरमा और नीम तेल कर घोल बनाय के छिड़काव करू।",
            "Bhojpuri": "ट्राइकोडरमा (5 ग्राम/लीटर) आ 5% नीम के तेल के छिड़काव करीं।",
            "Bengali": "ট্রাইকোডার্মা (৫ গ্রাম/লিটার) ও ৫% নিম বীজের নির্যাস স্প্রে করুন।",
            "Marathi": "ट्रायकोडेर्मा (५ ग्रॅम/लीटर) आणि ५% कडुनिंब अर्काची फवारणी करा.",
            "Telugu": "ట్రైకోడెర్మా (5 గ్రా/లీ) మరియు 5% వేప నూనె పిచికారీ చేయండి.",
            "Tamil": "ட்ரைக்கோடெர்மா (5 கிராம்/லிட்டர்) மற்றும் வேப்ப எண்ணெய் தெளிக்கவும்.",
            "Gujarati": "ટ્રાઇકોડર્મા (5 ગ્રામ/લીટર) અને 5% લીમડાના અર્કનો છંટકાવ કરો.",
            "Punjabi": "ਟ੍ਰਾਈਕੋਡਰਮਾ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਅਤੇ 5% ਨੀਮ ਦੇ ਅਰਕ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Apply Trichoderma harzianum @ 5 g/L combined with 5% cold-pressed Neem Seed Kernel Extract (NSKE)."
        },
        "chemical": {
            "Hindi": "डाइफेनोकोनाज़ोल 25% EC @ 0.5 मिली/लीटर या क्लोरोथैलोनिल 75% WP @ 2 ग्राम/लीटर का छिड़काव करें।",
            "English": "Apply Difenoconazole 25% EC @ 0.5 ml/L or Chlorothalonil 75% WP @ 2.0 g/L at initial symptom onset."
        },
        "prevention": {
            "Hindi": "प्रमाणित रोगमुक्त कंद लगाएं, संतुलित पोटाश खाद दें और फसल चक्र अपनाएं।",
            "English": "Plant certified disease-free tubers, ensure balanced potash fertilization, and rotate with non-solanaceous crops."
        }
    },
    "Squash___Powdery_mildew": {
        "crop": {"Hindi": "कुम्हड़ा (स्क्वैश)", "English": "Squash"},
        "disease": {"Hindi": "चूर्णिल आसिता (पाउडरी मिल्ड्यू)", "English": "Powdery Mildew"},
        "organic": {
            "Hindi": "बेकिंग सोडा (5 ग्राम/लीटर) + 5 मिली नीम तेल को पानी में मिलाकर पत्तियों पर छिड़कें। खट्टी छाछ का घोल भी असरदार है।",
            "Khortha": "बेकिंग सोडा (5 ग्राम/लीटर) और नीम तेल मिलाय के छिड़काव करा।",
            "Nagpuri": "बेकिंग सोडा और नीम तेल कर पानी में घोल बनाय के छिड़काव करू।",
            "Bhojpuri": "बेकिंग सोडा (5 ग्राम/लीटर) आ नीम के तेल के घोल छिड़कीं।",
            "Bengali": "বেকিং সোডা (৫ গ্রাম/লিটার) ও নিম তেল জলে মিশিয়ে স্প্রে করুন।",
            "Marathi": "बेकिंग सोडा (५ ग्रॅम/लीटर) आणि कडुनिंब तेलाची पानांवर फवारणी करा.",
            "Telugu": "వంట సోడా (5 గ్రా/లీ) మరియు వేప నూనె కలిపి పిచికారీ చేయండి.",
            "Tamil": "பேக்கிங் சோடா (5 கிராம்/லிட்டர்) மற்றும் வேப்ப எண்ணெய் தெளிக்கவும்.",
            "Gujarati": "બેકિંગ સોડા (5 ગ્રામ/લીટર) અને લીમડાના તેલનું મિશ્રણ છાંટો.",
            "Punjabi": "ਬੇਕਿੰਗ ਸੋਡਾ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਅਤੇ ਨੀਮ ਦੇ ਤੇਲ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Spray baking soda (5 g/L) with 5 ml neem oil per liter, or fermented buttermilk solution on foliar canopy."
        },
        "chemical": {
            "Hindi": "घुलनशील गंधक (सल्फर 80% WP @ 2.5 ग्राम/लीटर) या एजोक्सीस्ट्रोबिन 23% SC @ 1 मिली/लीटर का छिड़काव करें।",
            "English": "Apply wettable sulfur 80% WP @ 2.5 g/L or Azoxystrobin 23% SC @ 1.0 ml/L at first appearance of white powdery patches."
        },
        "prevention": {
            "Hindi": "पौधों के बीच पर्याप्त दूरी रखें, टपक (ड्रिप) सिंचाई अपनाएं और पत्तियों को सूखा रखें।",
            "English": "Ensure wide plant spacing, use drip irrigation to prevent wet foliage, and maintain good field sanitation."
        }
    },
    "Strawberry___Leaf_scorch": {
        "crop": {"Hindi": "स्ट्रॉबेरी", "English": "Strawberry"},
        "disease": {"Hindi": "पत्ती झुलसन (लीफ स्कॉर्च)", "English": "Leaf Scorch"},
        "organic": {
            "Hindi": "कॉपर आधारित जैविक कवकनाशी या 5% नीम तेल का छिड़काव करें। पुरानी व संक्रमित पत्तियों को काटकर हटा दें।",
            "Khortha": "कॉपर जैविक दवाई चाहे 5% नीम तेल के छिड़काव करा। सड़ा पात छांट देब।",
            "Nagpuri": "कॉपर जैविक दवाई चाहे नीम तेल कर छिड़काव करू। खराब पात के हटा देबू।",
            "Bhojpuri": "कॉपर जैविक दवाई भा 5% नीम के तेल छिड़कीं। सड़ा पतोई हटा दीं।",
            "Bengali": "কপার জৈব ছত্রাকনাশক বা ৫% নিম তেল স্প্রে করুন। পুরনো আক্রান্ত পাতা ছেঁটে ফেলুন।",
            "Marathi": "ताम्रयुक्त सेंद्रिय बुरशीनाशक किंवा ५% कडुनिंब तेल फवारा. जुनी बाधित पाने छाटा.",
            "Telugu": "కాపర్ ఆధారిత జీవ శిలీంధ్రనాశిని లేదా 5% వేప నూనె పిచికారీ చేయండి.",
            "Tamil": "காப்பர் அடிப்படையிலான இயற்கை பூஞ்சைக் கொல்லி அல்லது 5% வேப்ப எண்ணெய் தெளிக்கவும்.",
            "Gujarati": "કોપર આધારિત જૈવિક ફૂગનાશક અથવા 5% લીમડાનું તેલ છાંટો.",
            "Punjabi": "ਕਾਪਰ ਅਧਾਰਤ ਜੈਵਿਕ ਉੱਲੀਨਾਸ਼ਕ ਜਾਂ 5% ਨੀਮ ਦੇ ਤੇਲ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Apply copper-based organic fungicide or 5% neem extract. Prune and destroy dead or spotted older leaves."
        },
        "chemical": {
            "Hindi": "कैप्टन 50% WP @ 2.5 ग्राम/लीटर या थायोफेनेट मिथाइल 70% WP @ 1 ग्राम/लीटर का छिड़काव करें।",
            "English": "Apply Captan 50% WP @ 2.5 g/L or Thiophanate methyl 70% WP @ 1.0 g/L at early vegetative stage."
        },
        "prevention": {
            "Hindi": "स्ट्रॉ मल्चिंग का उपयोग करें, ऊपर से पानी देने से बचें और पौधे अधिक घने न लगाएं।",
            "English": "Apply clean straw mulch, avoid overhead sprinkler irrigation, and maintain proper plant spacing."
        }
    },
    "Tomato___Late_blight": {
        "crop": {"Hindi": "टमाटर", "English": "Tomato"},
        "disease": {"Hindi": "पछेता झुलसा (लेट ब्लाइट)", "English": "Late Blight"},
        "organic": {
            "Hindi": "कॉपर हाइड्रोक्साइड 53.8% DF @ 2 ग्राम/लीटर या 1% बोर्डो मिश्रण का छिड़काव करें। संक्रमित पत्तियों को तुरंत जलाएं।",
            "Khortha": "कॉपर हाइड्रोक्साइड चाहे 1% बोर्डो मिश्रण के छिड़काव करा। खराब पात के तुरंत जलाय देब।",
            "Nagpuri": "कॉपर हाइड्रोक्साइड चाहे बोर्डो मिश्रण कर छिड़काव करू। बीमारी वाला पात के हटा देबू।",
            "Bhojpuri": "कॉपर हाइड्रोक्साइड भा 1% बोर्डो मिश्रण छिड़कीं। सड़ा पतोई तुरंत जलाईं।",
            "Bengali": "কপার হাইড্রোক্সাইড (২ গ্রাম/লিটার) বা ১% বোর্দো মিশ্রণ স্প্রে করুন। আক্রান্ত পাতা পুড়িয়ে ফেলুন।",
            "Marathi": "कॉपर हायड्रॉक्साईड (२ ग्रॅम/लीटर) किंवा १% बोर्डो मिश्रणाची फवारणी करा. बाधित पाने जाळून नष्ट करा.",
            "Telugu": "కాపర్ హైడ్రాక్సైడ్ (2 గ్రా/లీ) లేదా 1% బోర్డో మిశ్రమం పిచికారీ చేయండి.",
            "Tamil": "காப்பர் ஹைட்ராக்சைடு (2 கிராம்/லிட்டர்) அல்லது 1% போர்டோ கலவை தெளிக்கவும்.",
            "Gujarati": "કોપર હાઇડ્રોક્સાઇડ (2 ગ્રામ/લીટર) અથવા 1% બોર્ડો મિશ્રણનો છંટકાવ કરો.",
            "Punjabi": "ਕਾਪਰ ਹਾਈਡ੍ਰੋਕਸਾਈਡ (2 ਗ੍ਰਾਮ/ਲੀਟਰ) ਜਾਂ 1% ਬੋਰਡੋ ਮਿਸ਼ਰਣ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
            "English": "Apply Copper Hydroxide 53.8% DF @ 2.0 g/L or 1% Bordeaux Mixture. Immediately remove and destroy blighted foliage."
        },
        "chemical": {
            "Hindi": "साइमोक्सानिल 8% + मैंकोज़ेब 64% WP @ 2.5 ग्राम/लीटर या डाइमेथोमॉर्फ 50% WP @ 1.0 ग्राम/लीटर का 7-10 दिन के अंतराल पर छिड़काव करें।",
            "English": "Spray Cymoxanil 8% + Mancozeb 64% WP @ 2.5 g/L or Dimethomorph 50% WP @ 1.0 g/L at 7-10 day intervals under high blight risk."
        },
        "prevention": {
            "Hindi": "निचली 30 सेमी पत्तियां छांटें ताकि मिट्टी से संक्रमण न फैले, ड्रिप सिंचाई अपनाएं और फसल चक्र रखें।",
            "English": "Prune lower 30 cm canopy foliage touching soil, adopt drip irrigation, and avoid solanaceous crop rotation."
        }
    }
}


class FarmerAdvisoryEngine:
    """
    Multilingual Agronomic Advisory & Translation Engine with RAG & Sarvam AI Voice.
    """

    def __init__(self):
        self.rag_engine = AgriculturalRAGEngine()

    def translate_crop(self, crop_name: str, target_lang: str = "Hindi") -> str:
        return translate_crop(crop_name, target_lang)

    def translate_disease(self, disease_name: str, target_lang: str = "Hindi") -> str:
        return translate_disease(disease_name, target_lang)

    def translate_disease_class(self, disease_class: str, target_lang: str = "Hindi") -> tuple[str, str, str]:
        return translate_disease_class(disease_class, target_lang)

    def get_advisory(self, disease_class: str, is_low_confidence: bool = False, confidence_score: float = 0.0, target_lang: str = "Hindi") -> dict:
        """
        Fetches crop-specific advisory dynamically translated into target_lang.
        Guarantees that all crop names, disease titles, and remedies match target_lang.
        """
        rag_data = self.rag_engine.generate_grounded_advisory(disease_class, language=target_lang)
        dict_entry = MULTILINGUAL_DICTIONARY.get(disease_class, {})

        is_healthy = "healthy" in disease_class.lower()

        # 1. Resolve Multilingual Crop & Disease Names
        crop_disp, disease_disp, display_title = translate_disease_class(disease_class, target_lang)

        # Allow override from dict if explicitly present in target_lang
        if target_lang in dict_entry.get("crop", {}):
            crop_disp = dict_entry["crop"][target_lang]
        if target_lang in dict_entry.get("disease", {}):
            disease_disp = dict_entry["disease"][target_lang]
            display_title = f"{crop_disp} - {disease_disp}"

        # 2. Resolve Cause and Severity in selected language
        cs_info = CAUSE_SEVERITY_BY_LANG.get(target_lang, CAUSE_SEVERITY_BY_LANG.get("Hindi", CAUSE_SEVERITY_BY_LANG["English"]))
        cause_disp = cs_info["cause_healthy"] if is_healthy else cs_info["cause_disease"]
        severity_disp = cs_info["sev_healthy"] if is_healthy else cs_info["sev_disease"]

        # 3. Resolve Treatments
        if is_healthy:
            hm = HEALTHY_MESSAGES.get(target_lang, HEALTHY_MESSAGES["Hindi"])
            organic_disp = hm["organic"]
            chemical_disp = hm["chemical"]
            prevention_disp = hm["prevention"]
        else:
            # Check dictionary for target language first
            organic_dict = dict_entry.get("organic", {})
            chemical_dict = dict_entry.get("chemical", {})
            prevention_dict = dict_entry.get("prevention", {})

            if target_lang == "English":
                organic_disp = organic_dict.get("English") or rag_data.get("full_grounded_content", "Apply 5% Neem Seed Kernel Extract (NSKE) or Trichoderma harzianum @ 5 g/L.")
                chemical_disp = chemical_dict.get("English", "Apply Mancozeb 75% WP @ 2.5 g/L or Difenoconazole 25% EC @ 0.5 ml/L.")
                prevention_disp = prevention_dict.get("English", "Maintain 60 cm row spacing, practice crop rotation, and avoid overhead sprinkler watering.")
            else:
                # Regional language: check specific entry, fallback to Hindi if regional is missing, or localized fallback (never raw English RAG text)
                organic_disp = organic_dict.get(target_lang) or organic_dict.get("Hindi") or "5% नीम के बीज के अर्क (NSKE) या ट्राइकोडर्मा जैविक कवकनाशी का छिड़काव करें।"
                chemical_disp = chemical_dict.get(target_lang) or chemical_dict.get("Hindi") or "मैंकोज़ेब 75% WP @ 2.5 ग्राम/लीटर या अनुशंसित कवकनाशी का छिड़काव करें।"
                prevention_disp = prevention_dict.get(target_lang) or prevention_dict.get("Hindi") or "फसल चक्र अपनाएं, उचित दूरी रखें और ड्रिप सिंचाई का प्रयोग करें।"

        return {
            "crop": crop_disp,
            "disease": disease_disp,
            "is_healthy": is_healthy,
            "display_title": display_title,
            "cause": cause_disp,
            "severity": severity_disp,
            "organic_treatment": organic_disp,
            "chemical_treatment": chemical_disp,
            "prevention": prevention_disp,
            "sdg_impact": "Healthy crops ensure food security and zero chemical runoff (SDG 2 & 15).",
            "rag_title": rag_data.get("retrieved_title", "Agricultural Extension Advisory"),
            "source_agency": rag_data.get("source_agency", "ICAR Indian Council of Agricultural Research"),
            "citation": rag_data.get("citation", "ICAR Extension Manual (2023)."),
            "grounded_evidence": organic_disp
        }

    def get_voice_script_by_language(self, advisory_data: dict | str, lang_choice: str = "Hindi") -> str:
        """
        Retrieves natural voice text script for selected language.
        Accurately translates reassurance or disease warning into the chosen language.
        """
        if isinstance(advisory_data, str):
            advisory_data = self.get_advisory(advisory_data, target_lang=lang_choice)

        crop = advisory_data.get("crop", "फसल")
        disease = advisory_data.get("disease", "रोग")
        organic = advisory_data.get("organic_treatment", "")
        is_healthy = advisory_data.get("is_healthy", False) or "healthy" in str(disease).lower() or "स्वस्थ" in str(disease).lower() or "সুস্থ" in str(disease).lower() or "निरोगी" in str(disease).lower()

        lang_lower = lang_choice.lower()

        # Reassurance for healthy crop in selected language
        if is_healthy:
            if "english" in lang_lower:
                return f"Great news! Your {crop} crop is completely healthy and vigorous. No pesticide or chemical treatment is needed."
            elif "khortha" in lang_lower:
                return f"बधाई हो! तोहर {crop} के फसल एकदम बेस और स्वस्थ है। कोनो दवाई भा कीटनाशक के जरूरत नखे।"
            elif "nagpuri" in lang_lower:
                return f"बधाई! रउरे कर {crop} कर फसल पूरा स्वस्थ आहे। कोनो कीटनाशक कर दरकार नखे।"
            elif "bhojpuri" in lang_lower:
                return f"खुसखबरी! रउआ {crop} के फसल बिल्कुल ठीक आ स्वस्थ बा। कवनो कीटनाशक भा दवाई के जरूरत नइखे।"
            elif "bengali" in lang_lower:
                return f"অভিনন্দন! আপনার {crop} ফসল সম্পূর্ণ সুস্থ। কোনো কীটনাশক বা চিকিৎসার প্রয়োজন নেই।"
            elif "marathi" in lang_lower:
                return f"अभिनंदन! तुमचे {crop} पीक पूर्णपणे निरोगी आहे. कोणत्याही रासायनिक उपचारांची गरज नाही."
            elif "telugu" in lang_lower:
                return f"అభినందనలు! మీ {crop} పంట పూర్తిగా ఆరోగ్యకరంగా ఉంది. ఎలాంటి పురుగుమందులు అవసరం లేదు."
            elif "tamil" in lang_lower:
                return f"வாழ்த்துகள்! உங்கள் {crop} பயிர் ஆரோக்கியமாக உள்ளது. எந்த பூச்சிக்கொல்லியும் தேவையில்லை."
            elif "gujarati" in lang_lower:
                return f"અભિનંદન! તમારો {crop} પાક સંપૂર્ણ સ્વસ્થ છે. કોઈ જંતુનાશકની જરૂર નથી."
            elif "punjabi" in lang_lower:
                return f"ਵਧਾਈ ਹੋਵੇ! ਤੁਹਾਡੀ {crop} ਦੀ ਫ਼ਸਲ ਪੂਰੀ ਤਰ੍ਹਾਂ ਤੰਦਰੁਸਤ ਹੈ। ਕਿਸੇ ਕੀਟਨਾਸ਼ਕ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।"
            else:
                return f"बधाई हो! आपकी {crop} की फसल पूरी तरह स्वस्थ और सुरक्षित है। किसी भी कीटनाशक या रासायनिक उपचार की आवश्यकता नहीं है।"

        # Disease warning & remedy in selected language
        if "english" in lang_lower:
            return f"Warning: {disease} detected on {crop}. Recommended treatment: {organic}"
        elif "khortha" in lang_lower:
            return f"सावधान! {crop} के फसल में {disease} पावल गेल है। उपाय: {organic}"
        elif "nagpuri" in lang_lower:
            return f"सावधान! {crop} कर फसल में {disease} रोगा देखा गेलक। उपचार: {organic}"
        elif "bhojpuri" in lang_lower:
            return f"सावधान! {crop} के फसल में {disease} रोग लागल बा। उपचार: {organic}"
        elif "bengali" in lang_lower:
            return f"সতর্কতা! {crop} ফসলে {disease} শনাক্ত হয়েছে। প্রস্তাবিত প্রতিকার: {organic}"
        elif "marathi" in lang_lower:
            return f"सावधान! {crop} पिकावर {disease} आढळला आहे. शिफारस केलेले उपाय: {organic}"
        elif "telugu" in lang_lower:
            return f"హెచ్చరిక! {crop} పంటలో {disease} గుర్తించబడింది. సిఫార్సు చేసిన చికిత్స: {organic}"
        elif "tamil" in lang_lower:
            return f"எச்சரிக்கை! {crop} பயிரில் {disease} கண்டறியப்பட்டுள்ளது. பரிந்துரைக்கப்பட்ட சிகிச்சை: {organic}"
        elif "gujarati" in lang_lower:
            return f"સાવધાન! {crop} પાકમાં {disease} જોવા મળ્યો છે. ભલામણ કરેલ ઉપાય: {organic}"
        elif "punjabi" in lang_lower:
            return f"ਸਾਵਧਾਨ! {crop} ਦੀ ਫ਼ਸਲ ਵਿੱਚ {disease} ਪਾਇਆ ਗਿਆ ਹੈ। ਸਿਫਾਰਸ਼ ਕੀਤਾ ਇਲਾਜ: {organic}"
        else:
            return f"सावधान! आपकी {crop} की फसल में {disease} पाया गया है। अनुशंसित उपचार: {organic}"

    def get_sarvam_audio_bytes(self, text: str, language: str = "Hindi", pace: float = 1.0) -> bytes | None:
        """
        Generate speech audio bytes using Sarvam AI bulbul TTS service with standard natural pace (default 1.0).
        """
        try:
            api_key = os.getenv("SARVAM_API_KEY", "")
            if not api_key:
                return None

            lang_map = {
                "hindi": "hi-IN", "khortha": "hi-IN", "nagpuri": "hi-IN", "bhojpuri": "hi-IN",
                "english": "en-IN", "bengali": "bn-IN", "tamil": "ta-IN", "telugu": "te-IN",
                "marathi": "mr-IN", "gujarati": "gu-IN", "punjabi": "pa-IN"
            }
            lang_code = lang_map.get(language.lower(), "hi-IN")
            clean_text = text.replace("*", "").replace("#", "").strip()[:500]
            if not clean_text:
                return None

            resp = requests.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={
                    "api-subscription-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": [clean_text],
                    "target_language_code": lang_code,
                    "speaker": "shubh",
                    "model": "bulbul:v3",
                    "pace": pace
                },
                timeout=12
            )
            if resp.status_code == 200:
                audios = resp.json().get("audios", [])
                if audios and len(audios[0]) > 0:
                    return base64.b64decode(audios[0])
            else:
                print(f"[Sarvam TTS Note] HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        except Exception as e:
            print(f"[Sarvam TTS Warning] Could not synthesize audio: {e}")
            return None

    def get_audio_bytes(self, text: str, language: str = "Hindi", pace: float = 1.0) -> bytes | None:
        """
        Generate speech audio at default natural speed.
        Prioritizes high-fidelity Sarvam AI regional neural voice at default pace (1.0),
        with automatic zero-dependency fallback to gTTS (default speed).
        """
        if not text or not text.strip():
            return None

        # 1. Primary: High-fidelity Sarvam AI Neural Voice with default pace (1.0)
        try:
            sarvam_bytes = self.get_sarvam_audio_bytes(text, language=language, pace=pace)
            if sarvam_bytes and len(sarvam_bytes) > 1000:
                return sarvam_bytes
        except Exception as e:
            print(f"[TTS Fallback Note] Sarvam TTS attempt: {e}")

        # 2. Secondary: Reliable fallback to gTTS (default speed)
        try:
            from gtts import gTTS
            import io
            lang_map = {
                "english": "en",
                "bengali": "bn",
                "tamil": "ta",
                "telugu": "te",
                "marathi": "mr",
                "gujarati": "gu",
                "punjabi": "pa",
                "hindi": "hi",
                "khortha": "hi",
                "nagpuri": "hi",
                "bhojpuri": "hi"
            }
            lang_code = lang_map.get(language.lower(), "hi")
            clean_text = text.replace("*", "").replace("#", "").strip()
            if not clean_text:
                return None

            tts = gTTS(text=clean_text, lang=lang_code, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            print(f"[gTTS Warning] Could not synthesize audio: {e}")
            return None

    def ask_farming_expert(self, question: str, disease_context: str = None, language: str = "Hindi") -> str:
        if disease_context:
            query = f"{disease_context} {question}"
        else:
            query = question
        docs = self.rag_engine.retrieve("", query=query, top_k=1)
        if docs:
            return docs[0].get("grounded_content", "कृपया नजदीकी कृषि विशेषज्ञ से परामर्श करें।")
        return (
            "नमस्ते! आपके प्रश्न के लिए धन्यवाद। "
            "सर्वोत्तम सलाह के लिए अपने नजदीकी कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
        )


advisory = FarmerAdvisoryEngine()
advisory_db = advisory


def generate_sarvam_audio_html(text: str, language: str = "Hindi", pace: float = 1.0) -> str:
    """Generate an HTML audio player using Sarvam AI TTS at natural pace."""
    try:
        audio_bytes = advisory.get_sarvam_audio_bytes(text, language, pace=pace)
        if audio_bytes:
            b64 = base64.b64encode(audio_bytes).decode()
            return f"<audio controls autoplay src='data:audio/wav;base64,{b64}'></audio>"
    except Exception as e:
        print(f"[Sarvam HTML Warning] {e}")
    return ""


if __name__ == "__main__":
    print("[Testing Advisory Engine with Multilingual Support]")
    for lang in ["Hindi", "English", "Bengali", "Tamil", "Marathi"]:
        adv = advisory.get_advisory("Apple___Apple_scab", target_lang=lang)
        voice = advisory.get_voice_script_by_language(adv, lang_choice=lang)
        print(f"\nLanguage: {lang}")
        print(f"Title: {adv['display_title']}")
        print(f"Cause: {adv['cause']}")
        print(f"Severity: {adv['severity']}")
        print(f"Voice: {voice[:80]}...")
