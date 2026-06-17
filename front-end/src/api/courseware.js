import request from './request'

/** 获取某课程的课件列表 */
export function listCourseware(courseId) {
  return request.get('/api/courseware', { params: { course_id: courseId } })
}

/** 上传课件（需要 teacher/admin 角色） */
export function uploadCourseware(formData) {
  return request.post('/api/courseware/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** 获取课件详情 */
export function getCoursewareDetail(coursewareId) {
  return request.get(`/api/courseware/${coursewareId}`)
}

/** 获取课件分块列表 */
export function getCoursewareChunks(coursewareId) {
  return request.get(`/api/courseware/${coursewareId}/chunks`)
}

/** 删除课件 */
export function deleteCourseware(coursewareId) {
  return request.delete(`/api/courseware/${coursewareId}`)
}
