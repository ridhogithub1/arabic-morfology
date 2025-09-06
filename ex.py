
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import random
from collections import OrderedDict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Gemini API configuration
GEMINI_API_KEYS = [
    "AIzaSyABMns2VWw5IuV6PYJhG1TJbIHl6-iJGGk",
    "AIzaSyAPFGdmEGAolRlOLG53k8VVE3IdpuywfSs"
]
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_random_api_key():
    """Get a random API key from the list"""
    return random.choice(GEMINI_API_KEYS)

def analyze_arabic_morphology(text):
    """Analyze Arabic text morphology using Gemini API"""
    api_key = get_random_api_key()
    url = f"{GEMINI_TEXT_URL}?key={api_key}"
    
    prompt = f"""
    Please analyze the Arabic morphology of the following text: "{text}"

    For each word in the text, provide detailed morphological analysis following standard Arabic grammar rules.
    Be very careful with:
    1. Root identification (الجذر) - extract the original 3 root letters correctly
    2. Pattern recognition (الوزن) - identify if it's فَعَلَ، فَعِلَ، فَعُلَ etc.
    3. Verb conjugation rules based on the correct pattern
    4. Handle weak verbs (معتل) and sound verbs (صحيح) appropriately

    For each word provide:
    1. الكلمة الأصلية (Original word)
    2. الجذر (Root letters - exactly 3 letters)
    3. حرف الزيادة (Extra letters if present, or ––– if none)
    4. الوزن (Pattern/Weight like فَعَلَ، فَعِلَ، فَعُلَ)
    5. نوع الكلمة (Word type: فعل ثلاثي مجرد/فعل/اسم/حرف)
    6. الزمن (For verbs: ماضٍ/مضارع/أمر)
    7. كلمات مشتقة (Related/derived words from the same root)
    8. المعنى (Meaning in Arabic and English)

    Please format your response as a JSON object with the following structure:
    {{
        "analysis": [
            {{
                "word": "الكلمة",
                "root": "ج ذ ر",
                "extra_letters": ["ا"] or "–––", 
                "pattern": "الوزن",
                "type": "نوع الكلمة",
                "tense": "الزمن (if applicable)",
                "related_words": ["كلمة1", "كلمة2", "كلمة3"],
                "meaning_arabic": "المعنى بالعربية",
                "meaning_english": "English meaning"
            }}
        ],
        "summary": "ملخص عام عن النص المُحلل"
    }}

    IMPORTANT: Be extremely careful with root identification. For example:
    - وَمِقَ has root و م ق (not و ق ف)
    - ضَرَبَ has root ض ر ب
    - Make sure to identify the correct pattern (فَعَلَ، فَعِلَ، فَعُلَ)

    Respond only with the JSON object, no additional text.
    """
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Try to parse the JSON response
            try:
                # Clean the response if it contains markdown code blocks
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                morphology_data = json.loads(content)
                return morphology_data
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw content
                return {
                    "error": "Could not parse JSON response",
                    "raw_response": content,
                    "analysis": [],
                    "summary": "تعذر تحليل النص بشكل صحيح"
                }
        else:
            return {
                "error": "No response from Gemini API",
                "analysis": [],
                "summary": "لم يتم الحصول على رد من الخدمة"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "analysis": [],
            "summary": "حدث خطأ في الاتصال بالخدمة"
        }

@app.route('/')
def home():
    return jsonify({"message": "Arabic Morphology API is running!"})

@app.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "No text provided",
                "message": "يرجى إدخال نص للتحليل"
            }), 400
        
        arabic_text = data['text'].strip()
        
        if not arabic_text:
            return jsonify({
                "error": "Empty text",
                "message": "النص فارغ"
            }), 400
        
        # Analyze the text
        result = analyze_arabic_morphology(arabic_text)
        
        return jsonify({
            "success": True,
            "input_text": arabic_text,
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "message": "حدث خطأ في الخادم"
        }), 500

def get_verb_patterns(root, pattern_type):
    """
    Get correct Arabic verb patterns based on root and pattern type.
    This function handles the morphological rules more accurately.
    """
    if len(root) < 3:
        return None
        
    # Split root into individual letters
    r1, r2, r3 = root[0], root[1], root[2]
    
    # Check if it's a weak verb (contains و، ي، ا)
    weak_letters = ['و', 'ي', 'ا', 'ء']
    is_weak = any(letter in weak_letters for letter in [r1, r2, r3])
    
    patterns = {}
    
    if pattern_type == "فَعَلَ_يَفْعُلُ":  # Rule 1: نَصَرَ pattern
        patterns = {
            "past": f"{r1}َ{r2}َ{r3}َ",
            "present": f"يَ{r1}ْ{r2}ُ{r3}ُ",
            "masdar": f"{r1}َ{r2}ْ{r3}ٌ",
            "masdar_mimi": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "ism_fael": f"{r1}َا{r2}ِ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اُ{r1}ْ{r2}ُ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}ُ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "alat": f"مِ{r1}ْ{r2}َ{r3}ٌ"
        }
    elif pattern_type == "فَعَلَ_يَفْعِلُ":  # Rule 2: ضَرَبَ pattern
        patterns = {
            "past": f"{r1}َ{r2}َ{r3}َ",
            "present": f"يَ{r1}ْ{r2}ِ{r3}ُ",
            "masdar": f"{r1}َ{r2}ْ{r3}ًا",
            "masdar_mimi": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "ism_fael": f"{r1}َا{r2}ِ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اِ{r1}ْ{r2}ِ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}ِ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "alat": f"مِ{r1}ْ{r2}َ{r3}ٌ"
        }
    elif pattern_type == "فَعَلَ_يَفْعَلُ":  # Rule 3: فَتَحَ pattern
        patterns = {
            "past": f"{r1}َ{r2}َ{r3}َ",
            "present": f"يَ{r1}ْ{r2}َ{r3}ُ",
            "masdar": f"{r1}َ{r2}ْ{r3}ًا",
            "masdar_mimi": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "ism_fael": f"{r1}َا{r2}ِ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اِ{r1}ْ{r2}َ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}َ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "alat": f"مِ{r1}ْ{r2}ا{r3}ٌ"
        }
    elif pattern_type == "فَعِلَ_يَفْعَلُ":  # Rule 4: عَلِمَ pattern
        patterns = {
            "past": f"{r1}َ{r2}ِ{r3}َ",
            "present": f"يَ{r1}ْ{r2}َ{r3}ُ",
            "masdar": f"{r1}ِ{r2}ْ{r3}ًا",
            "masdar_mimi": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "ism_fael": f"{r1}َا{r2}ِ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اِ{r1}ْ{r2}َ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}َ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "alat": "–––"
        }
    elif pattern_type == "فَعُلَ_يَفْعُلُ":  # Rule 5: حَسُنَ pattern
        patterns = {
            "past": f"{r1}َ{r2}ُ{r3}َ",
            "present": f"يَ{r1}ْ{r2}ُ{r3}ُ",
            "masdar": f"{r1}ُ{r2}ْ{r3}ًا",
            "masdar_mimi": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "ism_fael": f"{r1}َ{r2}َ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اُ{r1}ْ{r2}ُ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}ُ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}َ{r3}ٌ",
            "alat": "–––"
        }
    elif pattern_type == "فَعِلَ_يَفْعِلُ":  # Rule 6: حَسِبَ pattern
        patterns = {
            "past": f"{r1}َ{r2}ِ{r3}َ",
            "present": f"يَ{r1}ْ{r2}ِ{r3}ُ",
            "masdar": f"{r1}ِ{r2}َا{r3}ًا",
            "masdar_mimi": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "ism_fael": f"{r1}َا{r2}ِ{r3}ٌ",
            "ism_mafool": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "amr": f"اِ{r1}ْ{r2}ِ{r3}ْ",
            "nahi": f"لَا تَ{r1}ْ{r2}ِ{r3}ْ",
            "zaman": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "makan": f"مَ{r1}ْ{r2}ِ{r3}ٌ",
            "alat": f"{r1}َا{r2}ُو{r3}ٌ" if root == "حسب" else "–––"
        }
    
    # Handle weak verbs specially
    if is_weak:
        patterns = handle_weak_verbs(root, pattern_type, patterns)
    
    return patterns

def handle_weak_verbs(root, pattern_type, base_patterns):
    """Handle weak verbs (معتل) with special conjugation rules"""
    r1, r2, r3 = root[0], root[1], root[2]
    
    # Check type of weakness
    if r3 in ['و', 'ي']:  # ناقص (defective)
        if root == "رضي":
            base_patterns.update({
                "present": "يَرْضَى",
                "masdar": "رِضًا",
                "masdar_mimi": "مَرْضًى",
                "ism_fael": "رَاضٍ",
                "ism_mafool": "مَرْضِيٌّ",
                "amr": "اِرْضَ",
                "nahi": "لَا تَرْضَ",
                "zaman": "مَرْضًى",
                "makan": "مَرْضًى"
            })
    elif r2 in ['و', 'ي']:  # أجوف (hollow)
        # Handle hollow verbs like قال، باع
        pass
    elif r1 in ['و', 'ي', 'ا']:  # مثال (assimilated)
        if root == "وعد":
            base_patterns.update({
                "amr": "عِدْ",
                "present": "يَعِدُ"
            })
    
    return base_patterns

def get_correct_pattern_by_root(root):
    """
    Determine the correct pattern based on the root.
    This uses a more comprehensive mapping based on Arabic morphological rules.
    """
    pattern_mapping = {
        # Pattern 1: فَعَلَ - يَفْعُلُ
        "نصر": "فَعَلَ_يَفْعُلُ", "كتب": "فَعَلَ_يَفْعُلُ",
        
        # Pattern 2: فَعَلَ - يَفْعِلُ  
        "ضرب": "فَعَلَ_يَفْعِلُ", "جلس": "فَعَلَ_يَفْعِلُ",
        
        # Pattern 3: فَعَلَ - يَفْعَلُ
        "فتح": "فَعَلَ_يَفْعَلُ", "ذهب": "فَعَلَ_يَفْعَلُ",
        
        # Pattern 4: فَعِلَ - يَفْعَلُ
        "علم": "فَعِلَ_يَفْعَلُ", "شرب": "فَعِلَ_يَفْعَلُ",
        
        # Pattern 5: فَعُلَ - يَفْعُلُ
        "حسن": "فَعُلَ_يَفْعُلُ", "كرم": "فَعُلَ_يَفْعُلُ",
        
        # Pattern 6: فَعِلَ - يَفْعِلُ
        "حسب": "فَعِلَ_يَفْعِلُ", "ورث": "فَعِلَ_يَفْعِلُ",
        
        # Weak verbs
        "رضي": "فَعِلَ_يَفْعَلُ", "وعد": "فَعَلَ_يَفْعِلُ",
        "وقف": "فَعَلَ_يَفْعِلُ", "ومق": "فَعِلَ_يَفْعَلُ"
    }
    
    # Convert root from "ض ر ب" format to "ضرب"
    clean_root = root.replace(" ", "")
    
    return pattern_mapping.get(clean_root, "فَعَلَ_يَفْعِلُ")  # Default

@app.route('/tasrif', methods=['POST'])
def generate_tasrif():
    try:
        data = request.get_json()
        if not data or 'root' not in data or 'mode' not in data:
            return jsonify({"error": "Need root and mode"}), 400

        # Clean the root input
        root = data['root'].strip().replace(' ', '')
        mode = data['mode']

        if len(root) < 3:
            return jsonify({"error": "Invalid root"}), 400

        if mode == "istilahi":
            # Get the correct pattern for this root
            pattern_type = get_correct_pattern_by_root(root)
            patterns = get_verb_patterns(root, pattern_type)
            
            if not patterns:
                return jsonify({"error": "Could not generate patterns"}), 400
            
            tasrif_data = [
                ("الماضي", patterns["past"]),
                ("المضارع", patterns["present"]),
                ("المصدر", patterns["masdar"]),
                ("المصدر الميمي", patterns["masdar_mimi"]),
                ("اسم الفاعل", patterns["ism_fael"]),
                ("اسم المفعول", patterns["ism_mafool"]),
                ("فعل الأمر", patterns["amr"]),
                ("فعل النهي", patterns["nahi"]),
                ("اسم الزمان", patterns["zaman"]),
                ("اسم المكان", patterns["makan"]),
                ("اسم الآلة", patterns["alat"]),
            ]
        
        elif mode == "lughowiy":
            # Generate correct conjugations for different subjects
            r1, r2, r3 = root[0], root[1], root[2]
            pattern_type = get_correct_pattern_by_root(root)
            
            # Get the base past tense form
            if pattern_type.startswith("فَعِلَ"):
                base_pattern = f"{r1}َ{r2}ِ{r3}َ"
            elif pattern_type.startswith("فَعُلَ"):
                base_pattern = f"{r1}َ{r2}ُ{r3}َ"
            else:  # فَعَلَ
                base_pattern = f"{r1}َ{r2}َ{r3}َ"
            
            # Handle weak verbs for lughowiy conjugation
            if root in ["رضي"]:
                tasrif_data = [
                    ("هو", "رَضِيَ"),
                    ("هما (م)", "رَضِيَا"),
                    ("هم", "رَضُوا"),
                    ("هي", "رَضِيَتْ"),
                    ("هما (ف)", "رَضِيَتَا"),
                    ("هن", "رَضِينَ"),
                    ("أنتَ", "رَضِيتَ"),
                    ("أنتما (م)", "رَضِيتُمَا"),
                    ("أنتم", "رَضِيتُمْ"),
                    ("أنتِ", "رَضِيتِ"),
                    ("أنتما (ف)", "رَضِيتُمَا"),
                    ("أنتن", "رَضِيتُنَّ"),
                    ("أنا", "رَضِيتُ"),
                    ("نحن", "رَضِينَا"),
                ]
            elif root in ["حسن"]:
                tasrif_data = [
                    ("هو", "حَسُنَ"),
                    ("هما (م)", "حَسُنَا"),
                    ("هم", "حَسُنُوا"),
                    ("هي", "حَسُنَتْ"),
                    ("هما (ف)", "حَسُنَتَا"),
                    ("هن", "حَسُنَّ"),
                    ("أنتَ", "حَسُنْتَ"),
                    ("أنتما (م)", "حَسُنْتُمَا"),
                    ("أنتم", "حَسُنْتُمْ"),
                    ("أنتِ", "حَسُنْتِ"),
                    ("أنتما (ف)", "حَسُنْتُمَا"),
                    ("أنتن", "حَسُنْتُنَّ"),
                    ("أنا", "حَسُنْتُ"),
                    ("نحن", "حَسُنَّا"),
                ]
            else:
                # Standard conjugation for sound verbs
                tasrif_data = [
                    ("هو", base_pattern),
                    ("هما (م)", f"{r1}َ{r2}َ{r3}َا" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}َا"),
                    ("هم", f"{r1}َ{r2}َ{r3}ُوا" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ُوا"),
                    ("هي", f"{base_pattern}تْ"),
                    ("هما (ف)", f"{base_pattern}تَا"),
                    ("هن", f"{r1}َ{r2}َ{r3}ْنَ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْنَ"),
                    ("أنتَ", f"{r1}َ{r2}َ{r3}ْتَ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتَ"),
                    ("أنتما (م)", f"{r1}َ{r2}َ{r3}ْتُمَا" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتُمَا"),
                    ("أنتم", f"{r1}َ{r2}َ{r3}ْتُمْ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتُمْ"),
                    ("أنتِ", f"{r1}َ{r2}َ{r3}ْتِ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتِ"),
                    ("أنتما (ف)", f"{r1}َ{r2}َ{r3}ْتُمَا" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتُمَا"),
                    ("أنتن", f"{r1}َ{r2}َ{r3}ْتُنَّ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتُنَّ"),
                    ("أنا", f"{r1}َ{r2}َ{r3}ْتُ" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْتُ"),
                    ("نحن", f"{r1}َ{r2}َ{r3}ْنَا" if not pattern_type.startswith("فَعُلَ") else f"{r1}َ{r2}ُ{r3}ْنَا"),
                ]
        else:
            return jsonify({"error": "Invalid mode"}), 400

        return jsonify({"success": True, "tasrif": tasrif_data, "root": root})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)