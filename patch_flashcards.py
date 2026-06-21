import os

file_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\flashcards.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the HTML dropdown in the header
old_dropdown_html = """<select id="flashcardFilter" onchange="renderFlashcards()" class="pl-10 pr-8 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-56 shadow-sm transition-all appearance-none cursor-pointer">
                                <option value="all">All Sub-Courses</option>
                            </select>"""
new_dropdown_html = """<select id="flashcardFilter" onchange="fetchFilteredFlashcards()" class="pl-10 pr-8 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-56 shadow-sm transition-all appearance-none cursor-pointer">
                                <option value="" disabled selected>Select a Sub-Course</option>
                            </select>"""
content = content.replace(old_dropdown_html, new_dropdown_html)

# 2. Update populateCourseDropdowns
old_populate = """            const filterOptions = '<option value="all">All Sub-Courses</option>' + options;"""
new_populate = """            const filterOptions = '<option value="" disabled selected>Select a Sub-Course</option>' + options;
            const mcqFilterOptions = '<option value="all">All Sub-Courses</option>' + options;"""
content = content.replace(old_populate, new_populate)

old_fc_filter = """if(flashcardFilter) flashcardFilter.innerHTML = filterOptions;
            if(mcqFilter) mcqFilter.innerHTML = filterOptions;"""
new_fc_filter = """if(flashcardFilter) flashcardFilter.innerHTML = filterOptions;
            if(mcqFilter) mcqFilter.innerHTML = mcqFilterOptions;"""
content = content.replace(old_fc_filter, new_fc_filter)

old_val_fc_filter = """const valFcFilter = flashcardFilter ? flashcardFilter.value : 'all';"""
new_val_fc_filter = """const valFcFilter = flashcardFilter ? flashcardFilter.value : '';"""
content = content.replace(old_val_fc_filter, new_val_fc_filter)


# 3. Add fetchFilteredFlashcards()
fetch_func = """async function fetchFilteredFlashcards() {
            const filterCourseId = document.getElementById('flashcardFilter').value;
            const tbody = document.getElementById('flashcardTableBody');
            
            if (!filterCourseId) {
                state.flashcards = [];
                renderFlashcards();
                return;
            }
            
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><div class="flex justify-center items-center gap-2"><div class="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>Loading...</div></td></tr>';
            
            const fData = await apiCall(`learning/admin/flashcards/?subcourse_id=${filterCourseId}`);
            if (fData) {
                state.flashcards = fData.results || fData;
                renderFlashcards();
            } else {
                state.flashcards = [];
                renderFlashcards();
            }
        }
"""
content = content.replace("function renderFlashcards() {", fetch_func + "\nfunction renderFlashcards() {")

# 4. Update renderFlashcards()
old_render = """function renderFlashcards() {
            const tbody = document.getElementById('flashcardTableBody');
            const filterCourseId = document.getElementById('flashcardFilter').value;
            
            const filtered = state.flashcards.filter(f => {
                if (filterCourseId === 'all') return true;
                return f.subcourse.toString() === filterCourseId;
            });

            tbody.innerHTML = filtered.map(f => {
                const courseName = state.courses.find(c => c.id === f.subcourse)?.title || 'Unknown';
                return `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4"><input type="checkbox" value="${f.id}" class="row-checkbox-flashcard w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn('flashcard')"></td>
                    <td class="px-6 py-4 text-slate-500 font-medium">#${f.id}</td>"""

new_render = """function renderFlashcards() {
            const tbody = document.getElementById('flashcardTableBody');
            
            if (state.flashcards.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">No flashcards found. Select a sub-course to load data.</td></tr>';
                return;
            }

            tbody.innerHTML = state.flashcards.map((f, index) => {
                const courseName = state.courses.find(c => c.id === f.subcourse)?.title || 'Unknown';
                return `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4"><input type="checkbox" value="${f.id}" class="row-checkbox-flashcard w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn('flashcard')"></td>
                    <td class="px-6 py-4 text-slate-500 font-medium text-lg">#${index + 1}</td>"""

content = content.replace(old_render, new_render)

# 5. Update DOMContentLoaded
old_dom = """document.addEventListener('DOMContentLoaded', async () => {
const cData = await apiCall('learning/admin/subcourses/'); if(cData) { state.courses = cData.results || cData; populateCourseDropdowns(); } const fData = await apiCall('learning/admin/flashcards/'); if(fData){ state.flashcards = fData.results || fData; renderFlashcards(); }
});"""

new_dom = """document.addEventListener('DOMContentLoaded', async () => {
    const cData = await apiCall('learning/admin/subcourses/'); 
    if(cData) { 
        state.courses = cData.results || cData; 
        populateCourseDropdowns(); 
    } 
    state.flashcards = [];
    renderFlashcards();
});"""

content = content.replace(old_dom, new_dom)


# Also ensure AdminFlashcardViewSet has get_queryset filtering by subcourse_id if not already present
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("flashcards.html patched successfully.")
