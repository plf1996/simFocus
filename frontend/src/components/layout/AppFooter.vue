<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-left">
        <span class="copyright">
          &copy; {{ currentYear }} simFocus. All rights reserved.
        </span>
      </div>

      <div class="footer-center">
        <router-link to="/about" class="footer-link">About</router-link>
        <router-link to="/privacy" class="footer-link">Privacy</router-link>
        <router-link to="/terms" class="footer-link">Terms</router-link>
        <router-link to="/contact" class="footer-link">Contact</router-link>
      </div>

      <div class="footer-right">
        <el-tooltip content="GitHub" placement="top">
          <a href="https://github.com/simfocus" target="_blank" rel="noopener" class="footer-social">
            <el-icon :size="18">
              <Platform />
            </el-icon>
          </a>
        </el-tooltip>
        <el-tooltip content="Twitter" placement="top">
          <a href="https://twitter.com/simfocus" target="_blank" rel="noopener" class="footer-social">
            <el-icon :size="18">
              <ChatDotSquare />
            </el-icon>
          </a>
        </el-tooltip>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Platform, ChatDotSquare } from '@element-plus/icons-vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped lang="scss">
.app-footer {
  height: var(--footer-height, 50px);
  background-color: var(--el-bg-color-page);
  border-top: 1px solid var(--el-border-color-light);
  padding: 0 24px;
  display: flex;
  align-items: center;
  margin-top: auto;
}

.footer-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.footer-left {
  .copyright {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

.footer-center {
  display: flex;
  align-items: center;
  gap: 24px;
}

.footer-link {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  text-decoration: none;
  transition: color 0.2s;

  &:hover {
    color: var(--el-color-primary);
  }
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-social {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }
}

@media (max-width: 768px) {
  .app-footer {
    padding: 12px 16px;
    height: auto;
  }

  .footer-content {
    flex-direction: column;
    gap: 8px;
  }

  .footer-center {
    gap: 16px;
  }
}
</style>
