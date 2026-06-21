import os
import re

file_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\mcqs.html'

with open(file_path, 'r', encoding='utf-8') as f:
    cont = f.read()

# 1. Add Image and Voice HTML inputs
media_inputs = """                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-semibold text-slate-700 mb-2">Image (Optional)</label>
                                    <input type="file" id="mcqImage" accept="image/*"
                                        class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer">
                                </div>
                                <div>
                                    <label class="block text-sm font-semibold text-slate-700 mb-2">Voice (Optional)</label>
                                    <input type="file" id="mcqVoice" accept="audio/*"
                                        class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer">
                                </div>
                            </div>
"""

if "mcqImage" not in cont:
    cont = cont.replace(
        """                            <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">""",
        media_inputs + """\n                            <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">"""
    )


# 2. Update submitMCQ to use FormData
# Original:
#             const payload = { 
#                 subcourse: parseInt(document.getElementById('mcqCourseId').value), 
#                 text: document.getElementById('mcqQuestionText').value,
#                 incoming_options: incoming_options
#             };
# 
#             const method = editMode ? 'PUT' : 'POST';
#             const endpoint = editMode ? `learning/admin/mcqs/${currentEditId}/` : 'learning/admin/mcqs/';
#             
#             const res = await apiCall(endpoint, method, payload);

new_submit = """            const formData = new FormData();
            formData.append('subcourse', document.getElementById('mcqCourseId').value);
            formData.append('text', document.getElementById('mcqQuestionText').value);
            formData.append('incoming_options', JSON.stringify(incoming_options));
            
            const imgFile = document.getElementById('mcqImage').files[0];
            if (imgFile) formData.append('image', imgFile);
            
            const voiceFile = document.getElementById('mcqVoice').files[0];
            if (voiceFile) formData.append('voice', voiceFile);

            const method = editMode ? 'PUT' : 'POST';
            const endpoint = editMode ? `learning/admin/mcqs/${currentEditId}/` : 'learning/admin/mcqs/';
            
            const res = await apiCall(endpoint, method, formData);"""

cont = re.sub(
    r"const payload = \{[\s\S]*?const res = await apiCall\(endpoint, method, payload\);",
    new_submit,
    cont
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(cont)
