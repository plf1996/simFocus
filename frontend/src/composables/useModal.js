import { ref } from 'vue'

// Modal state
const modalState = ref({
  show: false,
  title: '',
  message: '',
  confirmText: '确定',
  cancelText: '取消',
  showConfirm: true,
  showCancel: true,
  confirmType: 'primary',
  resolve: null,
  reject: null
})

// Toast state
const toastState = ref({
  show: false,
  message: '',
  type: 'info'
})

export function useModal() {
  const showConfirm = (message, options = {}) => {
    return new Promise((resolve, reject) => {
      modalState.value = {
        show: true,
        title: options.title || '确认',
        message,
        confirmText: options.confirmText || '确定',
        cancelText: options.cancelText || '取消',
        showConfirm: options.showConfirm !== false,
        showCancel: options.showCancel !== false,
        showClose: options.showClose !== false,
        confirmType: options.confirmType || 'primary',
        resolve,
        reject
      }
    })
  }

  const showAlert = (message, options = {}) => {
    return new Promise((resolve) => {
      modalState.value = {
        show: true,
        title: options.title || '提示',
        message,
        confirmText: options.confirmText || '确定',
        cancelText: options.cancelText || '取消',
        showConfirm: true,
        showCancel: false,
        showClose: options.showClose !== false,
        confirmType: options.confirmType || 'primary',
        resolve,
        reject: null
      }
    })
  }

  const handleConfirm = () => {
    if (modalState.value.resolve) {
      modalState.value.resolve(true)
    }
    modalState.value.show = false
  }

  const handleCancel = () => {
    if (modalState.value.reject) {
      modalState.value.reject(false)
    }
    if (modalState.value.resolve && !modalState.value.showCancel) {
      modalState.value.resolve(true)
    }
    modalState.value.show = false
  }

  const showToast = (message, type = 'info', duration = 3000) => {
    toastState.value = {
      show: true,
      message,
      type
    }

    if (duration > 0) {
      setTimeout(() => {
        toastState.value.show = false
      }, duration)
    }
  }

  const closeToast = () => {
    toastState.value.show = false
  }

  return {
    modalState,
    toastState,
    showConfirm,
    showAlert,
    handleConfirm,
    handleCancel,
    showToast,
    closeToast
  }
}
