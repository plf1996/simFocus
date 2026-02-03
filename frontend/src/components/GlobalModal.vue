<template>
  <CommonModal
    :show="modalState.show"
    :title="modalState.title"
    :message="modalState.message"
    :confirm-text="modalState.confirmText"
    :cancel-text="modalState.cancelText"
    :show-confirm="modalState.showConfirm"
    :show-cancel="modalState.showCancel"
    :show-close="modalState.showClose"
    :confirm-type="modalState.confirmType"
    @confirm="handleConfirm"
    @cancel="handleCancel"
    @close="handleCancel"
  />

  <Toast
    :show="toastState.show"
    :message="toastState.message"
    :type="toastState.type"
    @close="closeToast"
  />
</template>

<script setup>
import { useModal } from '@/composables/useModal'
import CommonModal from './CommonModal.vue'
import Toast from './Toast.vue'

const {
  modalState,
  toastState,
  handleConfirm,
  handleCancel,
  closeToast
} = useModal()
</script>
