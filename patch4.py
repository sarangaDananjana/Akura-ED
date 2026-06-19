import re

filepath_html = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\dashboard.html'
filepath_py = r'c:\Users\Saranga\Desktop\Akura ED\learning\views.py'

# --- 1. PATCH dashboard.html ---
with open(filepath_html, 'r', encoding='utf-8') as f:
    content_html = f.read()

# Update apiCall
old_api = """        async function apiCall(endpoint, method = 'GET', body = null) {
            const options = { method, headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);"""
new_api = """        async function apiCall(endpoint, method = 'GET', body = null) {
            const options = { method, headers: { 'Authorization': `Bearer ${token}` } };
            if (body) {
                if (body instanceof FormData) {
                    options.body = body;
                } else {
                    options.headers['Content-Type'] = 'application/json';
                    options.body = JSON.stringify(body);
                }
            }"""
content_html = content_html.replace(old_api, new_api)

# Update Flashcard Modal HTML
old_modal = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Question Text</label>
                        <textarea id="fcQuestion" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>"""
new_modal = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Question Text</label>
                        <textarea id="fcQuestion" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-2">Question Image (Optional)</label>
                            <input type="file" id="fcQuestionImage" accept="image/*" class="w-full border border-slate-200 rounded-xl px-4 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-2">Question Audio (Optional)</label>
                            <input type="file" id="fcQuestionVoice" accept="audio/*" class="w-full border border-slate-200 rounded-xl px-4 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer">
                        </div>
                    </div>"""
content_html = content_html.replace(old_modal, new_modal)

# Update submitFlashcard JS
old_submit = """        async function submitFlashcard(e) {
            e.preventDefault();
            const payload = { subcourse: parseInt(document.getElementById('fcCourseId').value), question_text: document.getElementById('fcQuestion').value, answer: document.getElementById('fcShortAnswer').value, answer_text: document.getElementById('fcAnswer').value, is_premium_only: document.getElementById('fcPremium').checked };
            const method = editMode ? 'PUT' : 'POST';
            const endpoint = editMode ? `learning/admin/flashcards/${currentEditId}/` : 'learning/admin/flashcards/';
            const res = await apiCall(endpoint, method, payload);"""
new_submit = """        async function submitFlashcard(e) {
            e.preventDefault();
            const formData = new FormData();
            formData.append('subcourse', document.getElementById('fcCourseId').value);
            formData.append('question_text', document.getElementById('fcQuestion').value);
            formData.append('answer', document.getElementById('fcShortAnswer').value);
            formData.append('answer_text', document.getElementById('fcAnswer').value);
            formData.append('is_premium_only', document.getElementById('fcPremium').checked);
            
            const qImage = document.getElementById('fcQuestionImage').files[0];
            if (qImage) formData.append('question_image', qImage);
            const qVoice = document.getElementById('fcQuestionVoice').files[0];
            if (qVoice) formData.append('question_voice', qVoice);

            const method = editMode ? 'PUT' : 'POST';
            const endpoint = editMode ? `learning/admin/flashcards/${currentEditId}/` : 'learning/admin/flashcards/';
            
            // For FormData with PUT, some backends (like Django REST framework) have issues unless you spoof it or use PATCH.
            // Let's use PATCH for edit mode just in case, or stick to PUT.
            const res = await apiCall(endpoint, editMode ? 'PATCH' : 'POST', formData);"""
content_html = content_html.replace(old_submit, new_submit)

# Update editFlashcard JS
old_edit = """            document.getElementById('fcQuestion').value = f.question_text;
            document.getElementById('fcShortAnswer').value = f.answer || '';"""
new_edit = """            document.getElementById('fcQuestion').value = f.question_text;
            document.getElementById('fcShortAnswer').value = f.answer || '';
            document.getElementById('fcQuestionImage').value = '';
            document.getElementById('fcQuestionVoice').value = '';"""
content_html = content_html.replace(old_edit, new_edit)

with open(filepath_html, 'w', encoding='utf-8') as f:
    f.write(content_html)


# --- 2. PATCH views.py ---
with open(filepath_py, 'r', encoding='utf-8') as f:
    content_py = f.read()

# Fix header search logic
old_header = """            for idx, row in enumerate(rows):
                if row and any(cell.strip().lower() == 'question_id' for cell in row):
                    header_idx = idx
                    break
            
            if header_idx == -1:
                return Response({"error": "Could not find header row containing 'Question_ID'."}, status=status.HTTP_400_BAD_REQUEST)"""
new_header = """            for idx, row in enumerate(rows):
                if row and any(cell.strip().lower() in ['question_id', 'question_text'] for cell in row):
                    header_idx = idx
                    break
            
            if header_idx == -1:
                return Response({"error": "Could not find header row containing 'Question_ID' or 'Question_Text'."}, status=status.HTTP_400_BAD_REQUEST)"""
content_py = content_py.replace(old_header, new_header)

# Fix flashcard import logic
old_fc_import = """                    q_text = row_dict.get('Question_Text', '').strip()
                    ans_desc = row_dict.get('Correct_Description', '').strip()
                    
                    ans_text = ''
                    # Find the option with 'correct' status
                    for i in range(1, 6):
                        opt_status = row_dict.get(f'Status_{i}', '').strip().lower()
                        if opt_status == 'correct':
                            ans_text = row_dict.get(f'Option_{i}', '').strip()
                            break"""
new_fc_import = """                    q_text = row_dict.get('Question_Text', '').strip()
                    ans_desc = row_dict.get('Answer_Text', '').strip()
                    if not ans_desc:
                        ans_desc = row_dict.get('Correct_Description', '').strip()
                    
                    ans_text = row_dict.get('Answer', '').strip()
                    if not ans_text:
                        # Find the option with 'correct' status
                        for i in range(1, 6):
                            opt_status = row_dict.get(f'Status_{i}', '').strip().lower()
                            if opt_status == 'correct':
                                ans_text = row_dict.get(f'Option_{i}', '').strip()
                                break"""
content_py = content_py.replace(old_fc_import, new_fc_import)

with open(filepath_py, 'w', encoding='utf-8') as f:
    f.write(content_py)

print("Patch 4 applied.")
