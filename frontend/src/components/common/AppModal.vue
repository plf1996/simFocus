<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    :fullscreen="fullscreen"
    :top="top"
    :modal="modal"
    :modal-class="modalClass"
    :append-to-body="appendToBody"
    :lock-scroll="lockScroll"
    :custom-class="customClass"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :before-close="beforeClose"
    :draggable="draggable"
    :center="center"
    :align-center="alignCenter"
    @update:model-value="handleUpdate"
    @open="handleOpen"
    @close="handleClose"
    @opened="handleOpened"
    @closed="handleClosed"
  >
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>

    <div v-if="$slots.default" class="app-modal-body">
      <slot />
    </div>

    <template v-if="$slots.footer" #footer>
      <div class="app-modal-footer">
        <slot name="footer" />
      </div>
    </template>

    <template v-if="$slots.title" #title>
      <slot name="title" />
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  width?: string | number
  fullscreen?: boolean
  top?: string
  modal?: boolean
  modalClass?: string
  appendToBody?: boolean
  lockScroll?: boolean
  customClass?: string
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showClose?: boolean
  draggable?: boolean
  center?: boolean
  alignCenter?: boolean
  destroyOnClose?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '50%',
  fullscreen: false,
  modal: true,
  appendToBody: true,
  lockScroll: true,
  closeOnClickModal: true,
  closeOnPressEscape: true,
  showClose: true,
  draggable: false,
  center: false,
  alignCenter: true,
  destroyOnClose: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  open: []
  close: []
  opened: []
  closed: []
}>()

const handleUpdate = (value: boolean) => {
  emit('update:modelValue', value)
}

const handleOpen = () => {
  emit('open')
}

const handleClose = () => {
  emit('close')
}

const handleOpened = () => {
  emit('opened')
}

const handleClosed = () => {
  emit('closed')
}

const beforeClose = (done: () => void) => {
  handleClose()
  done()
}
</script>

<style scoped lang="scss">
.app-modal-body {
  max-height: 60vh;
  overflow-y: auto;
}

.app-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}
</style>
