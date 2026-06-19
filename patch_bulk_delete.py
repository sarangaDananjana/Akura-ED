import os
import re

dir_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel'

base_path = os.path.join(dir_path, 'base.html')

with open(base_path, 'r', encoding='utf-8') as f:
    base = f.read()

# Add shared Javascript
shared_js = """        function toggleSelectAll(masterCheckbox, type) {
            const checkboxes = document.querySelectorAll(`.row-checkbox-${type}`);
            checkboxes.forEach(cb => cb.checked = masterCheckbox.checked);
            updateBulkDeleteBtn(type);
        }

        function updateBulkDeleteBtn(type) {
            const checkboxes = document.querySelectorAll(`.row-checkbox-${type}:checked`);
            const btn = document.getElementById(`bulkDeleteBtn-${type}`);
            if (btn) {
                if (checkboxes.length > 0) {
                    btn.classList.remove('hidden');
                    btn.innerText = `Delete Selected (${checkboxes.length})`;
                } else {
                    btn.classList.add('hidden');
                }
            }
        }

        async function bulkDelete(type, baseUrl) {
            const checkboxes = document.querySelectorAll(`.row-checkbox-${type}:checked`);
            const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
            if (ids.length === 0) return;
            
            if (!confirm(`Are you sure you want to delete ${ids.length} items? This cannot be undone.`)) return;

            const btn = document.getElementById(`bulkDeleteBtn-${type}`);
            const origText = btn.innerText;
            btn.innerText = 'Deleting...';
            btn.disabled = true;

            const res = await apiCall(`${baseUrl}bulk_delete/`, 'DELETE', { ids: ids });
            if (res) {
                showToast(res.message || 'Items deleted successfully!');
                setTimeout(() => location.reload(), 800);
            } else {
                btn.innerText = origText;
                btn.disabled = false;
            }
        }"""

if "function toggleSelectAll" not in base:
    base = base.replace('// Set active nav button', shared_js + '\n\n        // Set active nav button')
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base)

# Pages to patch
configs = [
    {
        'file': 'domains.html',
        'type': 'domain',
        'url': 'learning/admin/domains/',
        'render_func_start': 'tbody.innerHTML = state.domains.map(d => `\n                <tr class="hover:bg-slate-50 transition-colors">',
        'header_th': '<th class="px-6 py-4">ID</th>',
        'buttons_div': '<div class="flex gap-2">',
    },
    {
        'file': 'courses.html',
        'type': 'parentcourse',
        'url': 'learning/admin/courses/',
        'render_func_start': 'tbody.innerHTML = state.parentcourses.map(c => {\n                const domainName = state.domains.find(d => d.id === c.domain)?.title || \'Unknown\';\n                return `\n                <tr class="hover:bg-slate-50 transition-colors">',
        'header_th': '<th class="px-6 py-4">ID</th>',
        'buttons_div': '<div class="flex gap-2">',
    },
    {
        'file': 'subcourses.html',
        'type': 'course',
        'url': 'learning/admin/subcourses/',
        'render_func_start': 'tbody.innerHTML = courses.map(c => {\n                const parentName = state.parentcourses.find(p => p.id === c.course)?.title || \'Unknown\';\n                return `\n                <tr class="hover:bg-slate-50 transition-colors">',
        'header_th': '<th class="px-6 py-4">ID</th>',
        'buttons_div': '<div class="flex gap-2">',
    },
    {
        'file': 'flashcards.html',
        'type': 'flashcard',
        'url': 'learning/admin/flashcards/',
        'render_func_start': 'tbody.innerHTML = filtered.map(f => {\n                const courseName = state.courses.find(c => c.id === f.subcourse)?.title || \'Unknown\';\n                return `\n                <tr class="hover:bg-slate-50 transition-colors">',
        'header_th': '<th class="px-6 py-4">ID</th>',
        'buttons_div': '<div class="flex gap-2">',
    },
    {
        'file': 'mcqs.html',
        'type': 'mcq',
        'url': 'learning/admin/mcqs/',
        'render_func_start': 'tbody.innerHTML = filtered.map(m => {\n                const courseName = state.courses.find(c => c.id === m.subcourse)?.title || \'Unknown\';\n                return `\n                <tr class="hover:bg-slate-50 transition-colors">',
        'header_th': '<th class="px-6 py-4">ID</th>',
        'buttons_div': '<div class="flex gap-2">',
    }
]

for cfg in configs:
    fp = os.path.join(dir_path, cfg['file'])
    with open(fp, 'r', encoding='utf-8') as f:
        cont = f.read()

    # 1. Add master checkbox
    th_repl = f'<th class="px-6 py-4 w-12"><input type="checkbox" onchange="toggleSelectAll(this, \'{cfg["type"]}\')" class="w-4 h-4 text-indigo-600 rounded border-slate-300"></th>\n                                    {cfg["header_th"]}'
    cont = cont.replace(cfg['header_th'], th_repl)

    # 2. Add row checkbox
    # We must match the tr start properly.
    if cfg['file'] in ['courses.html', 'subcourses.html', 'flashcards.html', 'mcqs.html']:
        # using regex to find the return ` <tr...
        patt = r'(return `\s*<tr class="hover:bg-slate-50 transition-colors">)'
        def repl(m):
            # what id property is it? 
            # In domains: d.id
            # courses: c.id
            # subcourses: c.id
            # flashcards: f.id
            # mcqs: m.id
            char = 'd'
            if cfg['type'] == 'parentcourse' or cfg['type'] == 'course': char = 'c'
            if cfg['type'] == 'flashcard': char = 'f'
            if cfg['type'] == 'mcq': char = 'm'
            
            return m.group(1) + f'\n                    <td class="px-6 py-4"><input type="checkbox" value="${{{char}.id}}" class="row-checkbox-{cfg["type"]} w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn(\'{cfg["type"]}\')"></td>'
        
        cont = re.sub(patt, repl, cont)
    else: # domains.html
        # map(d => ` <tr ...
        patt = r'(d => `\s*<tr class="hover:bg-slate-50 transition-colors">)'
        cont = re.sub(patt, r'\1\n                    <td class="px-6 py-4"><input type="checkbox" value="${d.id}" class="row-checkbox-' + cfg["type"] + r' w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn(\'' + cfg["type"] + r'\')"></td>', cont)


    # 3. Add bulk delete button
    btn_html = f'<button id="bulkDeleteBtn-{cfg["type"]}" onclick="bulkDelete(\'{cfg["type"]}\', \'{cfg["url"]}\')" class="hidden bg-red-50 text-red-600 border border-red-100 px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-red-100 transition-all shadow-sm"><i class="ph ph-trash"></i> Delete Selected</button>\n                            '
    cont = cont.replace(cfg['buttons_div'], cfg['buttons_div'] + '\n                            ' + btn_html)

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(cont)

print("UI templates patched successfully for Bulk Delete.")
