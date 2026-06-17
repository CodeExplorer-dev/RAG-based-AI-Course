import request from './request'

/** 获取当前用户的课程列表 */
export function listCourses() {
  return request.get('/api/courses')
}

/** 创建课程（需要 teacher/admin 角色） */
export function createCourse(data) {
  return request.post('/api/courses', data)
}

/** 通过选课码加入课程 */
export function joinCourse(joinCode) {
  return request.post('/api/courses/join', { join_code: joinCode })
}

/** 获取课程详情 */
export function getCourseDetail(courseId) {
  return request.get(`/api/courses/${courseId}`)
}

/** 获取课程学生列表（仅授课教师可查看） */
export function getCourseStudents(courseId) {
  return request.get(`/api/courses/${courseId}/students`)
}

/** 删除课程 */
export function deleteCourse(courseId) {
  return request.delete(`/api/courses/${courseId}`)
}
