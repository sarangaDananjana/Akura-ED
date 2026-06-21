import os

file_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\mcqs.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the HTML dropdown in the header
old_dropdown_html = """<select id="mcqFilter" onchange="renderMCQs()" class="pl-10 pr-8 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-56 shadow-sm transition-all appearance-none cursor-pointer">
                                <option value="all">All Sub-Courses</option>
                            </select>"""
new_dropdown_html = """<select id="mcqFilter" onchange="fetchFilteredMCQs()" class="pl-10 pr-8 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-56 shadow-sm transition-all appearance-none cursor-pointer">
                                <option value="" disabled selected>Select a Sub-Course</option>
                            </select>"""
content = content.replace(old_dropdown_html, new_dropdown_html)

# 2. Update populateCourseDropdowns
old_populate = """            const filterOptions = '<option value="all">All Sub-Courses</option>' + options;"""
new_populate = """            const filterOptions = '<option value="" disabled selected>Select a Sub-Course</option>' + options;
            const fcFilterOptions = '<option value="all">All Sub-Courses</option>' + options;"""
content = content.replace(old_populate, new_populate)

old_mcq_filter = """if(flashcardFilter) flashcardFilter.innerHTML = filterOptions;
            if(mcqFilter) mcqFilter.innerHTML = filterOptions;"""
new_mcq_filter = """if(flashcardFilter) flashcardFilter.innerHTML = fcFilterOptions;
            if(mcqFilter) mcqFilter.innerHTML = filterOptions;"""
content = content.replace(old_mcq_filter, new_mcq_filter)

old_val_mcq_filter = """const valMcqFilter = mcqFilter ? mcqFilter.value : 'all';"""
new_val_mcq_filter = """const valMcqFilter = mcqFilter ? mcqFilter.value : '';"""
content = content.replace(old_val_mcq_filter, new_val_mcq_filter)


# 3. Add fetchFilteredMCQs()
fetch_func = """async function fetchFilteredMCQs() {
            const filterCourseId = document.getElementById('mcqFilter').value;
            const tbody = document.getElementById('mcqTableBody');
            
            if (!filterCourseId) {
                state.mcqs = [];
                renderMCQs();
                return;
            }
            
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500"><div class="flex justify-center items-center gap-2"><div class="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>Loading...</div></td></tr>';
            
            const mData = await apiCall(`learning/admin/mcqs/?subcourse_id=${filterCourseId}`);
            if (mData) {
                state.mcqs = mData.results || mData;
                renderMCQs();
            } else {
                state.mcqs = [];
                renderMCQs();
            }
        }
"""
content = content.replace("function renderMCQs() {", fetch_func + "\nfunction renderMCQs() {")

# 4. Update renderMCQs()
old_render = """function renderMCQs() {
            const tbody = document.getElementById('mcqTableBody');
            const filterCourseId = document.getElementById('mcqFilter').value;
            
            const filtered = state.mcqs.filter(m => {
                if (filterCourseId === 'all') return true;
                return m.subcourse.toString() === filterCourseId;
            });

            tbody.innerHTML = filtered.map(m => {
                const courseName = state.courses.find(c => c.id === m.subcourse)?.title || 'Unknown';
                return `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4"><input type="checkbox" value="${m.id}" class="row-checkbox-mcq w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn('mcq')"></td>
                    <td class="px-6 py-4 text-slate-500 font-medium">#${m.id}</td>"""

new_render = """function renderMCQs() {
            const tbody = document.getElementById('mcqTableBody');
            
            if (state.mcqs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">No MCQs found. Select a sub-course to load data.</td></tr>';
                return;
            }

            tbody.innerHTML = state.mcqs.map((m, index) => {
                const courseName = state.courses.find(c => c.id === m.subcourse)?.title || 'Unknown';
                return `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4"><input type="checkbox" value="${m.id}" class="row-checkbox-mcq w-4 h-4 text-indigo-600 rounded border-slate-300" onchange="updateBulkDeleteBtn('mcq')"></td>
                    <td class="px-6 py-4 text-slate-500 font-medium text-lg">#${index + 1}</td>"""

content = content.replace(old_render, new_render)

# 5. Update DOMContentLoaded
old_dom = """document.addEventListener('DOMContentLoaded', async () => {
const cData = await apiCall('learning/admin/subcourses/'); if(cData) { state.courses = cData.results || cData; populateCourseDropdowns(); } const mData = await apiCall('learning/admin/mcqs/'); if(mData){ state.mcqs = mData.results || mData; renderMCQs(); }
});"""

new_dom = """document.addEventListener('DOMContentLoaded', async () => {
    const cData = await apiCall('learning/admin/subcourses/'); 
    if(cData) { 
        state.courses = cData.results || cData; 
        populateCourseDropdowns(); 
    } 
    state.mcqs = [];
    renderMCQs();
});"""

content = content.replace(old_dom, new_dom)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("mcqs.html patched successfully.")
