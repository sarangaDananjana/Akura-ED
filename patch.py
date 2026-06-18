import re

filepath = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update openModal
old_modal = """            if (modalId === 'parentCourseModal') {"""
new_modal = """            if (modalId === 'domainModal') {
                document.getElementById('domainModalTitle').innerText = isEdit ? 'Edit Domain' : 'Add Domain';
                document.getElementById('domainSubmitBtn').innerText = isEdit ? 'Update Domain' : 'Save Domain';
            } else if (modalId === 'parentCourseModal') {"""
content = content.replace(old_modal, new_modal)

# 2. Add populateDomainDropdowns and update populateParentCourseDropdowns
old_dropdowns = """        function populateParentCourseDropdowns() {
            const options = state.parentcourses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            document.getElementById('subcourseParentId').innerHTML = options;
        }"""
new_dropdowns = """        function populateDomainDropdowns() {
            const options = state.domains.map(d => `<option value="${d.id}">${d.title}</option>`).join('');
            const filterOptions = '<option value="all">All Domains</option>' + options;
            document.getElementById('pcDomainId').innerHTML = options;
            document.getElementById('courseDomainFilter').innerHTML = filterOptions;
        }

        function populateParentCourseDropdowns() {
            const options = state.parentcourses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            const filterOptions = '<option value="all">All Parent Courses</option>' + options;
            document.getElementById('subcourseParentId').innerHTML = options;
            document.getElementById('subcourseCourseFilter').innerHTML = filterOptions;
        }"""
content = content.replace(old_dropdowns, new_dropdowns)

# 3. Editing functions
old_edit = """        // 5. Editing Functions
        function editParentCourse(id) {"""
new_edit = """        // 5. Editing Functions
        function editDomain(id) {
            const d = state.domains.find(x => x.id === id);
            if(!d) return;
            currentEditId = id;
            document.getElementById('domainTitle').value = d.title;
            document.getElementById('domainDesc').value = d.description;
            document.getElementById('domainActive').checked = d.is_active;
            openModal('domainModal', true);
        }

        function editParentCourse(id) {"""
content = content.replace(old_edit, new_edit)

old_edit_pc = """            document.getElementById('parentCourseTitle').value = c.title;"""
new_edit_pc = """            document.getElementById('pcDomainId').value = c.domain;
            document.getElementById('parentCourseTitle').value = c.title;"""
content = content.replace(old_edit_pc, new_edit_pc)

# 4. loadAllData
old_load = """        async function loadAllData() {
            const pData = await apiCall('learning/admin/courses/');"""
new_load = """        async function loadAllData() {
            const dData = await apiCall('learning/admin/domains/');
            if (dData) { state.domains = dData.results || dData; document.getElementById('stat-domains').innerText = state.domains.length; renderDomains(); populateDomainDropdowns(); }

            // Apply domain filter to courses fetch if selected
            const domainFilter = document.getElementById('courseDomainFilter')?.value;
            let courseUrl = 'learning/admin/courses/';
            if (domainFilter && domainFilter !== 'all') { courseUrl += `?domain_id=${domainFilter}`; }

            const pData = await apiCall(courseUrl);"""
content = content.replace(old_load, new_load)

old_load_c = """            const cData = await apiCall('learning/admin/subcourses/');"""
new_load_c = """            const subcourseFilter = document.getElementById('subcourseCourseFilter')?.value;
            let subUrl = 'learning/admin/subcourses/';
            if (subcourseFilter && subcourseFilter !== 'all') { subUrl += `?course_id=${subcourseFilter}`; }
            const cData = await apiCall(subUrl);"""
content = content.replace(old_load_c, new_load_c)

# 5. Fetch Filtered Functions
old_render = """        function renderParentCourses() {"""
new_render = """        function fetchFilteredParentCourses() { loadAllData(); }
        function fetchFilteredCourses() { loadAllData(); }

        async function updateDomainPriority(id, val) {
            await apiCall(`learning/admin/domains/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Domain priority updated');
            loadAllData();
        }

        async function updateParentCoursePriority(id, val) {
            await apiCall(`learning/admin/courses/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Course priority updated');
            loadAllData();
        }

        async function updateCoursePriority(id, val) {
            await apiCall(`learning/admin/subcourses/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Sub-Course priority updated');
            loadAllData();
        }

        function renderDomains() {
            const tbody = document.getElementById('domainTableBody');
            tbody.innerHTML = state.domains.map(d => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4 text-slate-500 font-medium">#${d.id}</td>
                    <td class="px-6 py-4 font-bold text-slate-800">${d.title}</td>
                    <td class="px-6 py-4">
                        <input type="number" value="${d.priority || 0}" onchange="updateDomainPriority(${d.id}, this.value)" class="w-20 border border-slate-200 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-indigo-500">
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-md ${d.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}">
                            <span class="w-1.5 h-1.5 rounded-full ${d.is_active ? 'bg-emerald-500' : 'bg-slate-400'}"></span>
                            ${d.is_active ? 'Active' : 'Draft'}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-right whitespace-nowrap">
                        <button onclick="editDomain(${d.id})" class="text-slate-400 hover:text-blue-500 transition-colors p-2 rounded-lg hover:bg-blue-50"><i class="ph ph-pencil-simple text-lg"></i></button>
                        <button onclick="deleteDomain(${d.id})" class="text-slate-400 hover:text-red-500 transition-colors p-2 rounded-lg hover:bg-red-50"><i class="ph ph-trash text-lg"></i></button>
                    </td>
                </tr>
            `).join('');
        }

        function renderParentCourses() {"""
content = content.replace(old_render, new_render)

old_render_pc = """                    <td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>
                    <td class="px-6 py-4">"""
new_render_pc = """                    <td class="px-6 py-4 text-slate-500 font-medium">${state.domains.find(d => d.id === c.domain)?.title || 'Unknown'}</td>
                    <td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>
                    <td class="px-6 py-4">
                        <input type="number" value="${c.priority || 0}" onchange="updateParentCoursePriority(${c.id}, this.value)" class="w-20 border border-slate-200 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-indigo-500">
                    </td>
                    <td class="px-6 py-4">"""
content = content.replace(old_render_pc, new_render_pc)

# filter functions locally
old_filter_pc = """        function filterParentCourses() {"""
new_filter_pc = """        function filterParentCoursesLocally() {"""
content = content.replace(old_filter_pc, new_filter_pc)

# render Courses
old_render_c = """                    <td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>
                    <td class="px-6 py-4">"""
new_render_c = """                    <td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>
                    <td class="px-6 py-4">
                        <input type="number" value="${c.priority || 0}" onchange="updateCoursePriority(${c.id}, this.value)" class="w-20 border border-slate-200 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-indigo-500">
                    </td>
                    <td class="px-6 py-4">"""
# Only replace first occurrence (which is inside renderCourses)
# Wait, this matches both renderParentCourses (already modified) and renderCourses?
# renderParentCourses was already replaced. So this will hit renderCourses.
content = content.replace(old_render_c, new_render_c, 1)

old_filter_c = """        function filterCourses() {"""
new_filter_c = """        function filterCoursesLocally() {"""
content = content.replace(old_filter_c, new_filter_c)

# 6. Submits
old_submit = """        // 7. Submit Handlers
        async function submitParentCourse(e) {"""
new_submit = """        // 7. Submit Handlers
        async function submitDomain(e) {
            e.preventDefault();
            const payload = { title: document.getElementById('domainTitle').value, description: document.getElementById('domainDesc').value, is_active: document.getElementById('domainActive').checked };
            const method = editMode ? 'PUT' : 'POST';
            const endpoint = editMode ? `learning/admin/domains/${currentEditId}/` : 'learning/admin/domains/';
            const res = await apiCall(endpoint, method, payload);
            if (res) { showToast(editMode ? 'Domain updated!' : 'Domain added!'); closeModal('domainModal'); loadAllData(); }
        }

        async function submitParentCourse(e) {"""
content = content.replace(old_submit, new_submit)

old_submit_pc = """const payload = { title: document.getElementById('parentCourseTitle').value,"""
new_submit_pc = """const payload = { domain: parseInt(document.getElementById('pcDomainId').value), title: document.getElementById('parentCourseTitle').value,"""
content = content.replace(old_submit_pc, new_submit_pc)

# 7. Delete
old_delete = """        // 8. Delete Handlers
        async function deleteParentCourse(id) {"""
new_delete = """        // 8. Delete Handlers
        async function deleteDomain(id) { if (confirm('Delete this domain? It will delete ALL related courses.')) { await apiCall(`learning/admin/domains/${id}/`, 'DELETE'); loadAllData(); } }
        async function deleteParentCourse(id) {"""
content = content.replace(old_delete, new_delete)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
