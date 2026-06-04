<template>
  <div class="auth-page fixed top-navbar inset-x-0 bottom-0 flex items-center justify-center overflow-hidden">
    <div class="grid-overlay" aria-hidden="true" />
    <div class="deco-ring" aria-hidden="true" />

    <!-- 食材实物照片 -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <img
        src="/ingredients/rice.png"
        class="specimen specimen-a"
        alt=""
      />
      <img
        src="/ingredients/sichuan-pepper.png"
        class="specimen specimen-b"
        alt=""
      />
    </div>

    <div class="auth-panel glass-panel relative z-[4] w-[min(440px,92vw)] pt-[44px] px-12 pb-10 rounded-[20px]">
      <div class="accent-bar" aria-hidden="true" />
      <h2 class="text-center font-serif text-[24px] font-medium text-earth tracking-[0.10em] m-0 mb-0.5">注册账号</h2>
      <p class="text-center text-[12px] text-text-muted m-0 mb-8 tracking-[0.06em]">踏上寻味之旅，记录属于你的味觉版图</p>

      <form @submit.prevent="submit" class="flex flex-col gap-[18px]">
        <label class="flex flex-col gap-1.5">
          <span class="text-[12px] font-medium text-text-mid tracking-[0.05em]">用户名</span>
          <input
            v-model.trim="username"
            type="text"
            class="field-input h-11 rounded-[11px] border border-glass-border bg-[rgba(255,252,247,0.62)] px-4 font-sans text-base text-text outline-none transition-all duration-[220ms] ease"
            placeholder="2–32 位字符"
            autocomplete="username"
            required
          />
        </label>

        <label class="flex flex-col gap-1.5">
          <span class="text-[12px] font-medium text-text-mid tracking-[0.05em]">密码</span>
          <input
            v-model="password"
            type="password"
            class="field-input h-11 rounded-[11px] border border-glass-border bg-[rgba(255,252,247,0.62)] px-4 font-sans text-base text-text outline-none transition-all duration-[220ms] ease"
            placeholder="至少 4 位"
            autocomplete="new-password"
            required
          />
        </label>

        <Transition name="msg">
          <p v-if="errorMsg" class="text-[12px] text-carmine bg-carmine-soft rounded-lg py-[9px] px-[14px] m-0">{{ errorMsg }}</p>
        </Transition>

        <button type="submit" :disabled="busy" class="submit-btn h-12 rounded-[13px] border border-[rgba(139,94,52,0.12)] text-[#fffaf2] cursor-pointer font-sans text-base font-semibold tracking-[0.12em] mt-1 transition-all" :class="{ busy }">
          <span v-if="busy" class="inline-flex items-center gap-2.5">
            <span class="spinner" />
            注册中…
          </span>
          <span v-else>注册</span>
        </button>
      </form>

      <p class="flex items-center justify-center gap-2 mt-6 text-[12px] text-text-muted">
        <span class="inline-block w-1 h-1 rounded-full bg-leaf opacity-60" />
        已有账号？
        <RouterLink to="/login" class="text-earth font-medium no-underline hover:underline hover:underline-offset-[2px]">去登录</RouterLink>
      </p>
    </div>

    <div class="watermark" aria-hidden="true">REGISTER</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMsg = ref('')
const busy = ref(false)

async function submit() {
  errorMsg.value = ''
  if (!username.value || !password.value) { errorMsg.value = '请填写用户名和密码'; return }
  if (username.value.length < 2) { errorMsg.value = '用户名至少 2 位字符'; return }
  if (password.value.length < 4) { errorMsg.value = '密码至少 4 位'; return }

  busy.value = true
  try {
    const res = await authStore.register(username.value, password.value)
    if (res.ok) {
      router.push('/profile')
    } else {
      errorMsg.value = res.error || '注册失败，请重试'
    }
  } catch {
    errorMsg.value = '网络错误，请检查后端是否运行'
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KEPT — Tailwind cannot express these:
   multi-radial-gradient, mask-image, composite box-shadow rings,
   pseudo-elements, multi-stop button gradients, animations,
   clamp(), Vue transitions, responsive overrides
   ═══════════════════════════════════════════════════════════════ */

/* KEPT: multi-radial-gradient background */
.auth-page {
  background:
    radial-gradient(circle at 50% 44%, rgba(255, 252, 248, 0.68), transparent 34%),
    radial-gradient(circle at 86% 16%, rgba(94, 123, 80, 0.20), transparent 30%),
    radial-gradient(circle at 12% 78%, rgba(62, 120, 145, 0.13), transparent 28%),
    radial-gradient(circle at 50% 100%, rgba(169, 101, 53, 0.12), transparent 36%),
    linear-gradient(155deg, #f7efe3 0%, #eef3ed 52%, #fbf7ef 100%);
}

/* KEPT: mask-image grid pattern */
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

/* KEPT: composite box-shadow ring effect */
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

/* KEPT: filter drop-shadow + clamp + fadeUp animation */
.specimen {
  position: absolute;
  width: clamp(96px, 11vw, 180px);
  object-fit: contain;
  filter: drop-shadow(0 16px 36px rgba(83, 62, 36, 0.18)) saturate(0.92);
  opacity: 0.28;
  animation: fadeUp 1.3s ease 0.3s both;
}
.specimen-a {
  right: clamp(20px, 6vw, 90px);
  top: 8vh;
  transform: rotate(6deg);
}
.specimen-b {
  left: clamp(16px, 5vw, 68px);
  bottom: 12vh;
  transform: rotate(-14deg);
  animation-delay: 0.45s;
}

/* KEPT: radarIn animation (keyframes defined in global.css) */
.auth-panel {
  animation: radarIn 0.55s ease 0.15s both;
}

/* KEPT: multi-stop linear-gradient accent bar (leaf + saffron) */
.accent-bar {
  position: absolute;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  width: 54px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--leaf), var(--saffron), transparent);
  opacity: 0.74;
}

/* KEPT: pseudo-elements not reachable by Tailwind */
.field-input::placeholder { color: var(--text-muted); }
.field-input:focus {
  background: rgba(255, 252, 248, 0.96);
  box-shadow: 0 0 0 3px rgba(232, 169, 23, 0.22);
  border-color: rgba(232, 169, 23, 0.38);
}

/* KEPT: multi-stop gradient + composite box-shadow + hover/active/busy states */
.submit-btn {
  background: linear-gradient(135deg, var(--leaf) 0%, #4a6e3e 40%, var(--earth) 100%);
  box-shadow:
    0 14px 34px rgba(67, 92, 60, 0.20),
    inset 0 1px 0 rgba(255, 255, 255, 0.20);
}
.submit-btn:hover:not(.busy) {
  transform: translateY(-2px);
  box-shadow:
    0 20px 44px rgba(67, 92, 60, 0.28),
    0 0 28px rgba(201, 166, 70, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
  filter: saturate(1.04);
}
.submit-btn:active:not(.busy) { transform: scale(0.98); }
.submit-btn.busy {
  background: rgba(94, 123, 80, 0.44);
  cursor: not-allowed;
  box-shadow: none;
}

/* KEPT: spinner animation — Tailwind has no animation definition system */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* KEPT: clamp() values + transform — not expressible as Tailwind utilities */
.watermark {
  position: absolute;
  left: clamp(32px, 5vw, 80px);
  bottom: 6vh;
  color: rgba(32, 27, 22, 0.05);
  font-family: var(--font-sans);
  font-size: clamp(52px, 5vw, 96px);
  font-weight: 500;
  letter-spacing: 0.14em;
  transform: rotate(-6deg);
  pointer-events: none;
}

/* KEPT: Vue transition classes */
.msg-enter-active, .msg-leave-active { transition: all 200ms ease; }
.msg-enter-from, .msg-leave-to { opacity: 0; transform: translateY(-4px); }

/* KEPT: responsive overrides */
@media (max-width: 500px) {
  .auth-panel { padding: 36px 28px 32px; }
  .specimen { opacity: 0.18; width: clamp(64px, 18vw, 100px); }
  .watermark { display: none; }
}
</style>
