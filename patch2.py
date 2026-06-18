import re

filepath = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update populateDomainDropdowns
old_p1 = """        function populateDomainDropdowns() {
            const options = state.domains.map(d => `<option value="${d.id}">${d.title}</option>`).join('');
            const filterOptions = '<option value="all">All Domains</option>' + options;
            document.getElementById('pcDomainId').innerHTML = options;
            document.getElementById('courseDomainFilter').innerHTML = filterOptions;
        }"""
new_p1 = """        function populateDomainDropdowns() {
            const domainFilter = document.getElementById('courseDomainFilter');
            const pcDomainId = document.getElementById('pcDomainId');
            const currentFilterVal = domainFilter ? domainFilter.value : 'all';
            const currentPcVal = pcDomainId ? pcDomainId.value : '';

            const options = state.domains.map(d => `<option value="${d.id}">${d.title}</option>`).join('');
            const filterOptions = '<option value="all">All Domains</option>' + options;
            
            if(pcDomainId) pcDomainId.innerHTML = options;
            if(domainFilter) domainFilter.innerHTML = filterOptions;

            if(pcDomainId && currentPcVal) pcDomainId.value = currentPcVal;
            if(domainFilter && currentFilterVal) domainFilter.value = currentFilterVal;
        }"""
content = content.replace(old_p1, new_p1)

# 2. Update populateParentCourseDropdowns
old_p2 = """        function populateParentCourseDropdowns() {
            const options = state.parentcourses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            const filterOptions = '<option value="all">All Parent Courses</option>' + options;
            document.getElementById('subcourseParentId').innerHTML = options;
            document.getElementById('subcourseCourseFilter').innerHTML = filterOptions;
        }"""
new_p2 = """        function populateParentCourseDropdowns() {
            const parentId = document.getElementById('subcourseParentId');
            const courseFilter = document.getElementById('subcourseCourseFilter');
            const currentParentIdVal = parentId ? parentId.value : '';
            const currentFilterVal = courseFilter ? courseFilter.value : 'all';

            const options = state.parentcourses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            const filterOptions = '<option value="all">All Parent Courses</option>' + options;
            
            if(parentId) parentId.innerHTML = options;
            if(courseFilter) courseFilter.innerHTML = filterOptions;

            if(parentId && currentParentIdVal) parentId.value = currentParentIdVal;
            if(courseFilter && currentFilterVal) courseFilter.value = currentFilterVal;
        }"""
content = content.replace(old_p2, new_p2)

# 3. Update populateCourseDropdowns
old_p3 = """        function populateCourseDropdowns() {
            const options = state.courses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            const filterOptions = '<option value="all">All Sub-Courses</option>' + options;
            
            document.getElementById('fcCourseId').innerHTML = options;
            document.getElementById('mcqCourseId').innerHTML = options;
            document.getElementById('csvCourseId').innerHTML = options;
            document.getElementById('flashcardFilter').innerHTML = filterOptions;
            document.getElementById('mcqFilter').innerHTML = filterOptions;
        }"""
new_p3 = """        function populateCourseDropdowns() {
            const fcCourseId = document.getElementById('fcCourseId');
            const mcqCourseId = document.getElementById('mcqCourseId');
            const csvCourseId = document.getElementById('csvCourseId');
            const flashcardFilter = document.getElementById('flashcardFilter');
            const mcqFilter = document.getElementById('mcqFilter');

            const valFc = fcCourseId ? fcCourseId.value : '';
            const valMcq = mcqCourseId ? mcqCourseId.value : '';
            const valCsv = csvCourseId ? csvCourseId.value : '';
            const valFcFilter = flashcardFilter ? flashcardFilter.value : 'all';
            const valMcqFilter = mcqFilter ? mcqFilter.value : 'all';

            const options = state.courses.map(c => `<option value="${c.id}">${c.title}</option>`).join('');
            const filterOptions = '<option value="all">All Sub-Courses</option>' + options;
            
            if(fcCourseId) fcCourseId.innerHTML = options;
            if(mcqCourseId) mcqCourseId.innerHTML = options;
            if(csvCourseId) csvCourseId.innerHTML = options;
            if(flashcardFilter) flashcardFilter.innerHTML = filterOptions;
            if(mcqFilter) mcqFilter.innerHTML = filterOptions;

            if(fcCourseId && valFc) fcCourseId.value = valFc;
            if(mcqCourseId && valMcq) mcqCourseId.value = valMcq;
            if(csvCourseId && valCsv) csvCourseId.value = valCsv;
            if(flashcardFilter && valFcFilter) flashcardFilter.value = valFcFilter;
            if(mcqFilter && valMcqFilter) mcqFilter.value = valMcqFilter;
        }"""
content = content.replace(old_p3, new_p3)


old_load = """        function fetchFilteredParentCourses() { loadAllData(); }
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
        }"""
new_load = """        async function fetchFilteredParentCourses() {
            const domainFilter = document.getElementById('courseDomainFilter')?.value;
            let courseUrl = 'learning/admin/courses/';
            if (domainFilter && domainFilter !== 'all') { courseUrl += `?domain_id=${domainFilter}`; }
            const pData = await apiCall(courseUrl);
            if (pData) { state.parentcourses = pData.results || pData; document.getElementById('stat-parentcourses').innerText = state.parentcourses.length; renderParentCourses(); populateParentCourseDropdowns(); }
        }

        async function fetchFilteredCourses() {
            const subcourseFilter = document.getElementById('subcourseCourseFilter')?.value;
            let subUrl = 'learning/admin/subcourses/';
            if (subcourseFilter && subcourseFilter !== 'all') { subUrl += `?course_id=${subcourseFilter}`; }
            const cData = await apiCall(subUrl);
            if (cData) { state.courses = cData.results || cData; document.getElementById('stat-courses').innerText = state.courses.length; renderCourses(state.courses); populateCourseDropdowns(); }
        }

        async function updateDomainPriority(id, val) {
            await apiCall(`learning/admin/domains/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Domain priority updated');
            loadAllData();
        }

        async function updateParentCoursePriority(id, val) {
            await apiCall(`learning/admin/courses/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Course priority updated');
            fetchFilteredParentCourses();
        }

        async function updateCoursePriority(id, val) {
            await apiCall(`learning/admin/subcourses/${id}/`, 'PATCH', { priority: parseInt(val) });
            showToast('Sub-Course priority updated');
            fetchFilteredCourses();
        }"""
content = content.replace(old_load, new_load)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch 2 applied.")
