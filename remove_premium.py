import os

file_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\flashcards.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove Access Header
old_header = """                                    <th class="px-6 py-4">Question</th>
                                    <th class="px-6 py-4">Access</th>
                                    <th class="px-6 py-4 text-right">Actions</th>"""
new_header = """                                    <th class="px-6 py-4">Question</th>
                                    <th class="px-6 py-4 text-right">Actions</th>"""
content = content.replace(old_header, new_header)

# 2. Remove fcPremium input field in form
old_input = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Answer Description (Explanation)</label>
                        <textarea id="fcAnswer" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>
                    <label
                        class="flex items-center gap-3 p-4 border border-amber-100 bg-amber-50/50 rounded-xl cursor-pointer">
                        <input type="checkbox" id="fcPremium"
                            class="w-5 h-5 text-amber-500 border-amber-300 rounded focus:ring-amber-500">
                        <div>
                            <span class="block text-sm font-bold text-amber-900">Premium Only</span>
                            <span class="block text-xs text-amber-700 mt-0.5">Restrict access to paid users</span>
                        </div>
                    </label>
                </div>"""

new_input = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Answer Description (Explanation)</label>
                        <textarea id="fcAnswer" required rows="2"
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none resize-none"></textarea>
                    </div>
                </div>"""
content = content.replace(old_input, new_input)

# 3. Remove Access Column render logic
old_td = """                    <td class="px-6 py-4 font-medium text-slate-800">${f.question_text.substring(0, 50)}...</td>
                    <td class="px-6 py-4">
                        ${f.is_premium_only
                        ? '<span class="inline-flex items-center gap-1 text-xs font-bold text-amber-600 bg-amber-50 px-2.5 py-1 rounded-md"><i class="ph-fill ph-star"></i> Premium</span>'
                        : '<span class="inline-flex items-center text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">Free Plan</span>'}
                    </td>
                    <td class="px-6 py-4 text-right whitespace-nowrap">"""

new_td = """                    <td class="px-6 py-4 font-medium text-slate-800">${f.question_text.substring(0, 50)}...</td>
                    <td class="px-6 py-4 text-right whitespace-nowrap">"""
content = content.replace(old_td, new_td)

# 4. Remove from submitFlashcard
content = content.replace("formData.append('is_premium_only', document.getElementById('fcPremium').checked);\n            ", "")

# 5. Remove from editFlashcard
content = content.replace("document.getElementById('fcPremium').checked = f.is_premium_only;\n            ", "")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed premium only from flashcards.html")
