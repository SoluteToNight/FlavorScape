<template>
  <div class="auth-page">
    <div class="grid-overlay" aria-hidden="true" />
    <div class="deco-ring" aria-hidden="true" />

    <!-- 食材实物照片 -->
    <div class="specimen-layer" aria-hidden="true">
      <img
        src="/ingredients/chili.png"
        class="specimen specimen-a"
        alt=""
      />
      <img
        src="/ingredients/star-anise.png"
        class="specimen specimen-b"
        alt=""
      />
    </div>

    <div class="auth-panel glass-panel">
      <div class="accent-bar" aria-hidden="true" />
      <h2 class="panel-title">登录</h2>
      <p class="panel-subtitle">欢迎回到寻味地理</p>

      <form @submit.prevent="submit" class="auth-form">
        <label class="field">
          <span class="field-label">用户名</span>
          <input
            v-model.trim="username"
            type="text"
            class="field-input"
            placeholder="输入用户名"
            autocomplete="username"
            required
          />
        </label>

        <label class="field">
          <span class="field-label">密码</span>
          <input
            v-model="password"
            type="password"
            class="field-input"
            placeholder="输入密码"
            autocomplete="current-password"
            required
          />
        </label>

        <Transition name="msg">
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        </Transition>

        <button type="submit" :disabled="busy" class="submit-btn" :class="{ busy }">
          <span v-if="busy" class="spinner-wrap">
            <span class="spinner" />
            登录中…
          </span>
          <span v-else>登录</span>
        </button>
      </form>

      <p class="switch-line">
        <span class="switch-dot" />
        没有账号？
        <RouterLink to="/register" class="switch-link">去注册</RouterLink>
      </p>
    </div>

    <div class="watermark" aria-hidden="true">FLAVORSCAPE</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMsg = ref('')
const busy = ref(false)

async function submit() {
  errorMsg.value = ''
  if (!username.value || !password.value) { errorMsg.value = '请填写用户名和密码'; return }
  if (password.value.length < 4) { errorMsg.value = '密码至少 4 位'; return }

  busy.value = true
  try {
    const res = await authStore.login(username.value, password.value)
    if (res.ok) {
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      errorMsg.value = res.error || '登录失败，请重试'
    }
  } catch {
    errorMsg.value = '网络错误，请检查后端是否运行'
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: fixed;
  top: var(--navbar-h);
  inset-inline: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 44%, rgba(255, 252, 248, 0.68), transparent 34%),
    radial-gradient(circle at 14% 12%, rgba(94, 123, 80, 0.18), transparent 28%),
    radial-gradient(circle at 88% 82%, rgba(62, 120, 145, 0.14), transparent 30%),
    radial-gradient(circle at 50% 100%, rgba(169, 101, 53, 0.11), transparent 36%),
    linear-gradient(135deg, #fbf7ef 0%, #eef3ed 48%, #f7efe3 100%);
}

.grid-overlay {
  position: absolute;
  inset: -12%;
  background:
    linear-gradient(rgba(92, 75, 57, 0.032) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92, 75, 57, 0.026) 1px, transparent 1px);
  background-size: 88px 88px;
  mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,0.44), transparent 70%);
  pointer-events: none;
}

.deco-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(64vw, 680px);
  aspect-ratio: 1;
  border: 1px solid rgba(139, 94, 52, 0.10);
  border-radius: 50%;
  box-shadow:
    0 0 0 18px rgba(255, 252, 248, 0.08),
    0 0 0 62px rgba(94, 123, 80, 0.028),
    0 0 0 100px rgba(255, 252, 248, 0.04);
  transform: translate(-50%, -50%);
  pointer-events: none;
}

/* ── 食材实拍 ─────────────────────────────────────────────── */
.specimen-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.specimen {
  position: absolute;
  width: clamp(96px, 11vw, 180px);
  object-fit: contain;
  filter: drop-shadow(0 16px 36px rgba(83, 62, 36, 0.18)) saturate(0.92);
  opacity: 0.28;
  animation: fadeUp 1.3s ease 0.3s both;
}

.specimen-a {
  left: clamp(16px, 5vw, 72px);
  top: 10vh;
  transform: rotate(-10deg);
}

.specimen-b {
  right: clamp(20px, 6vw, 90px);
  bottom: 10vh;
  transform: rotate(14deg);
  animation-delay: 0.45s;
}

/* ── Panel ─────────────────────────────────────────────── */
.auth-panel {
  position: relative;
  z-index: 4;
  width: min(440px, 92vw);
  padding: 44px 48px 40px;
  border-radius: 20px;
  animation: radarIn 0.55s ease 0.15s both;
}

.accent-bar {
  position: absolute;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  width: 54px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--carmine), var(--saffron), transparent);
  opacity: 0.74;
}

.panel-title {
  text-align: center;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
  color: var(--earth);
  letter-spacing: 0.10em;
  margin: 0 0 2px;
}

.panel-subtitle {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 32px;
  letter-spacing: 0.06em;
}

/* ── Form ──────────────────────────────────────────────── */
.auth-form { display: flex; flex-direction: column; gap: 18px; }

.field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 12px; font-weight: 500;
  color: var(--text-mid); letter-spacing: 0.05em;
}

.field-input {
  height: 44px;
  border-radius: 11px;
  border: 1px solid var(--glass-border);
  background: rgba(255, 252, 247, 0.62);
  padding: 0 16px;
  font-family: var(--font-sans);
  font-size: 14px;
  color: var(--text);
  outline: none;
  transition: all 220ms ease;
}
.field-input::placeholder { color: var(--text-muted); }
.field-input:focus {
  background: rgba(255, 252, 248, 0.96);
  box-shadow: 0 0 0 3px rgba(232, 169, 23, 0.22);
  border-color: rgba(232, 169, 23, 0.38);
}

.error-msg {
  font-size: 12px;
  color: var(--carmine);
  background: var(--carmine-soft);
  border-radius: 8px;
  padding: 9px 14px;
  margin: 0;
}

.submit-btn {
  height: 48px;
  border: 1px solid rgba(139, 94, 52, 0.12);
  border-radius: 13px;
  background: linear-gradient(135deg, #8f4e37 0%, var(--earth) 45%, var(--leaf) 100%);
  box-shadow:
    0 14px 34px rgba(67, 92, 60, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.20);
  color: #fffaf2;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.12em;
  margin-top: 4px;
  transition: all var(--transition);
}
.submit-btn:hover:not(.busy) {
  transform: translateY(-2px);
  box-shadow:
    0 20px 44px rgba(67, 92, 60, 0.26),
    0 0 28px rgba(201, 166, 70, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
  filter: saturate(1.04);
}
.submit-btn:active:not(.busy) { transform: scale(0.98); }
.submit-btn.busy {
  background: rgba(139, 94, 52, 0.48);
  cursor: not-allowed;
  box-shadow: none;
}

.spinner-wrap { display: inline-flex; align-items: center; gap: 10px; }
.spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Switch ────────────────────────────────────────────── */
.switch-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  font-size: 12px;
  color: var(--text-muted);
}
.switch-dot {
  display: inline-block;
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--saffron);
  opacity: 0.6;
}
.switch-link {
  color: var(--earth);
  font-weight: 500;
  text-decoration: none;
}
.switch-link:hover { text-decoration: underline; text-underline-offset: 2px; }

.watermark {
  position: absolute;
  right: clamp(32px, 5vw, 80px);
  bottom: 6vh;
  color: rgba(32, 27, 22, 0.05);
  font-family: var(--font-sans);
  font-size: clamp(52px, 5vw, 96px);
  font-weight: 500;
  letter-spacing: 0.14em;
  transform: rotate(8deg);
  pointer-events: none;
}

.msg-enter-active, .msg-leave-active { transition: all 200ms ease; }
.msg-enter-from, .msg-leave-to { opacity: 0; transform: translateY(-4px); }

@media (max-width: 500px) {
  .auth-panel { padding: 36px 28px 32px; }
  .specimen { opacity: 0.18; width: clamp(64px, 18vw, 100px); }
  .watermark { display: none; }
}
</style>
