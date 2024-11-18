function showTab(tabName) {
    document.getElementById('myCourses').style.display = 'none';
    document.getElementById('addCourses').style.display = 'none';
    document.getElementById(tabName).style.display = 'block';
}

showTab('myCourses');
