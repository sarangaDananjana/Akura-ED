import re

filepath = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Flashcard Modal HTML
old_modal_html = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Answer Text</label>
                        <textarea id="fcAnswer" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>"""
new_modal_html = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Answer (Correct Option)</label>
                        <textarea id="fcShortAnswer" required rows="1"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Answer Description (Explanation)</label>
                        <textarea id="fcAnswer" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>"""
content = content.replace(old_modal_html, new_modal_html)

# 2. Update editFlashcard JS
old_edit_js = """            document.getElementById('fcCourseId').value = f.subcourse;
            document.getElementById('fcQuestion').value = f.question_text;
            document.getElementById('fcAnswer').value = f.answer_text;
            document.getElementById('fcPremium').checked = f.is_premium_only;"""
new_edit_js = """            document.getElementById('fcCourseId').value = f.subcourse;
            document.getElementById('fcQuestion').value = f.question_text;
            document.getElementById('fcShortAnswer').value = f.answer || '';
            document.getElementById('fcAnswer').value = f.answer_text;
            document.getElementById('fcPremium').checked = f.is_premium_only;"""
content = content.replace(old_edit_js, new_edit_js)

# 3. Update submitFlashcard JS
old_submit_js = """        async function submitFlashcard(e) {
            e.preventDefault();
            const payload = { subcourse: parseInt(document.getElementById('fcCourseId').value), question_text: document.getElementById('fcQuestion').value, answer_text: document.getElementById('fcAnswer').value, is_premium_only: document.getElementById('fcPremium').checked };"""
new_submit_js = """        async function submitFlashcard(e) {
            e.preventDefault();
            const payload = { subcourse: parseInt(document.getElementById('fcCourseId').value), question_text: document.getElementById('fcQuestion').value, answer: document.getElementById('fcShortAnswer').value, answer_text: document.getElementById('fcAnswer').value, is_premium_only: document.getElementById('fcPremium').checked };"""
content = content.replace(old_submit_js, new_submit_js)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch 3 applied.")
