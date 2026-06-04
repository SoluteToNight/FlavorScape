<template>
  <div class="profile-page fixed top-navbar inset-x-0 bottom-0 flex items-center justify-center overflow-hidden">
    <div class="grid-overlay" aria-hidden="true" />
    <div class="deco-ring-outer" aria-hidden="true" />
    <div class="deco-ring-inner" aria-hidden="true" />

    <!-- 食材实物照片 -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <img src="/ingredients/star-anise.png" class="specimen specimen-a" alt="" />
      <img src="/ingredients/rice.png" class="specimen specimen-b" alt="" />
    </div>

    <div class="cabinet glass-panel relative z-[4] w-[min(500px,93vw)] pt-[44px] px-12 pb-10 rounded-[20px]">
      <div class="accent-bar" aria-hidden="true" />

      <!-- Avatar -->
      <div class="flex flex-col items-center mb-6">
        <div class="relative w-[108px] aspect-square flex items-center justify-center mb-4">
          <span class="avat-ring avat-r1" />
          <span class="avat-ring avat-r2" />
          <img
            :src="avatarUrl"
            :alt="authStore.user?.username"
            class="avatar-img"
            referrerpolicy="no-referrer"
          />
        </div>
        <h2 class="font-serif text-[22px] font-medium text-earth tracking-[0.08em] m-0 mb-1">{{ authStore.user?.username }}</h2>
        <p class="inline-flex items-center gap-1.5 text-[12px] text-text-muted m-0">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="flex-shrink-0">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          注册于 {{ formattedDate }}
        </p>
      </div>

      <div class="flex items-center gap-3 mb-6">
        <span class="w-[5px] h-[5px] rounded-full bg-saffron opacity-50" />
        <span class="divider-line" />
        <span class="w-[5px] h-[5px] rounded-full bg-saffron opacity-50" />
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-3 mb-7">
        <div class="stat-card flex flex-col items-center gap-2 py-[18px] px-3 rounded-[14px] bg-[rgba(255,252,247,0.50)] border border-glass-border transition-all">
          <div class="stat-icon stat-icon-leaf">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
            </svg>
          </div>
          <div class="font-['Inter',sans-serif] text-[22px] font-light text-text leading-none">—</div>
          <div class="text-2xs text-text-muted tracking-[0.08em]">收藏节点</div>
        </div>
        <div class="stat-card flex flex-col items-center gap-2 py-[18px] px-3 rounded-[14px] bg-[rgba(255,252,247,0.50)] border border-glass-border transition-all">
          <div class="stat-icon stat-icon-water">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
            </svg>
          </div>
          <div class="font-['Inter',sans-serif] text-[22px] font-light text-text leading-none">—</div>
          <div class="text-2xs text-text-muted tracking-[0.08em]">探索路线</div>
        </div>
        <div class="stat-card flex flex-col items-center gap-2 py-[18px] px-3 rounded-[14px] bg-[rgba(255,252,247,0.50)] border border-glass-border transition-all">
          <div class="stat-icon stat-icon-amber">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 20V10M18 20V4M6 20v-4"/>
            </svg>
          </div>
          <div class="font-['Inter',sans-serif] text-[22px] font-light text-text leading-none">—</div>
          <div class="text-2xs text-text-muted tracking-[0.08em]">探索天数</div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col gap-2.5">
        <RouterLink to="/map" class="action-btn inline-flex items-center justify-center gap-2.5 h-[46px] rounded-[12px] font-sans text-base font-medium tracking-[0.08em] no-underline cursor-pointer transition-all action-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
          </svg>
          探索风味底图
        </RouterLink>

        <RouterLink to="/library" class="action-btn inline-flex items-center justify-center gap-2.5 h-[46px] rounded-[12px] font-sans text-base font-medium tracking-[0.08em] no-underline cursor-pointer transition-all action-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          浏览基因库
        </RouterLink>

        <button class="action-btn inline-flex items-center justify-center gap-2.5 h-[46px] rounded-[12px] font-sans text-base font-medium tracking-[0.08em] no-underline cursor-pointer transition-all action-danger" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          退出登录
        </button>
      </div>
    </div>

    <div class="watermark" aria-hidden="true">CABINET</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const avatarUrl = computed(() => {
  const name = encodeURIComponent(authStore.user?.username || '?')
  return `https://ui-avatars.com/api/?name=${name}&background=8B5E34&color=fff&size=160&bold=true&format=png`
})

const formattedDate = computed(() => {
  const raw = authStore.user?.created_at
  if (!raw) return '—'
  try {
    return new Date(raw).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return raw.split(' ')[0] || raw
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KEPT — Tailwind cannot express these:
   multi-radial-gradient, mask-image, composite box-shadow rings,
   filter drop-shadow, multi-stop gradients,
   pseudo-elements, complex hover effects, animations,
   clamp(), responsive overrides
   ═══════════════════════════════════════════════════════════════ */

/* KEPT: multi-radial-gradient background */
.profile-page {
  background:
    radial-gradient(circle at 50% 48%, rgba(255, 252, 248, 0.62), transparent 38%),
    radial-gradient(circle at 18% 20%, rgba(94, 123, 80, 0.19), transparent 30%),
    radial-gradient(circle at 84% 80%, rgba(62, 120, 145, 0.14), transparent 32%),
    radial-gradient(circle at 50% 96%, rgba(169, 101, 53, 0.14), transparent 34%),
    linear-gradient(135deg, #fbf7ef 0%, #eef3ed 46%, #f7efe3 100%);
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

/* KEPT: composite box-shadow ring effects */
.deco-ring-outer {
  position: absolute;
  left: 50%; top: 50%;
  width: min(72vw, 760px);
  aspect-ratio: 1;
  border: 1px solid rgba(139, 94, 52, 0.10);
  border-radius: 50%;
  box-shadow:
    0 0 0 16px rgba(255, 252, 248, 0.07),
    0 0 0 56px rgba(94, 123, 80, 0.025),
    0 0 0 92px rgba(255, 252, 248, 0.04);
  transform: translate(-50%, -50%);
  pointer-events: none;
}
.deco-ring-inner {
  position: absolute;
  left: 50%; top: 50%;
  width: min(44vw, 480px);
  aspect-ratio: 1;
  border: 1px dashed rgba(139, 94, 52, 0.13);
  border-radius: 50%;
  transform: translate(-50%, -50%) rotate(12deg);
  pointer-events: none;
}

/* KEPT: filter drop-shadow + clamp + fadeUp animation */
.specimen {
  position: absolute;
  width: clamp(96px, 11vw, 180px);
  object-fit: contain;
  filter: drop-shadow(0 16px 36px rgba(83, 62, 36, 0.18)) saturate(0.92);
  opacity: 0.26;
  animation: fadeUp 1.3s ease 0.3s both;
}
.specimen-a {
  left: clamp(22px, 5vw, 80px);
  top: 12vh;
  transform: rotate(-8deg);
}
.specimen-b {
  right: clamp(18px, 6vw, 96px);
  bottom: 10vh;
  transform: rotate(5deg);
  animation-delay: 0.45s;
}

/* KEPT: radarIn animation (keyframes defined in global.css) */
.cabinet {
  animation: radarIn 0.55s ease 0.15s both;
}

/* KEPT: multi-stop linear-gradient accent bar */
.accent-bar {
  position: absolute;
  left: 50%; top: 0;
  transform: translateX(-50%);
  width: 54px; height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--earth), var(--saffron), transparent);
  opacity: 0.74;
}

/* KEPT: avatar ring — composite box-shadow rings */
.avat-ring {
  position: absolute;
  border-radius: 50%;
}
.avat-r1 {
  inset: -6px;
  border: 1px solid rgba(139, 94, 52, 0.20);
  box-shadow: 0 0 0 10px rgba(255, 252, 248, 0.08);
}
.avat-r2 {
  inset: -16px;
  border: 1px dashed rgba(94, 123, 80, 0.22);
  transform: rotate(-14deg);
}

/* KEPT: composite box-shadow + border — Tailwind cannot express multi-layer shadow with inset */
.avatar-img {
  width: 80px;
  aspect-ratio: 1;
  border-radius: 50%;
  object-fit: cover;
  box-shadow:
    0 12px 34px rgba(67, 92, 60, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.24);
  border: 2px solid rgba(255, 252, 248, 0.6);
}

/* KEPT: gradient line — not expressible as Tailwind utility */
.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
}

/* KEPT: hover effects with composite transforms and box-shadows */
.stat-card:hover {
  transform: translateY(-3px);
  border-color: rgba(139, 94, 52, 0.18);
  box-shadow: 0 8px 28px rgba(51, 37, 22, 0.07);
}

/* KEPT: icon color variants — specific semi-transparent backgrounds paired with colors */
.stat-icon {
  width: 36px; aspect-ratio: 1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-icon-leaf  { background: rgba(94, 123, 80, 0.10);  color: var(--leaf); }
.stat-icon-water { background: rgba(62, 120, 145, 0.10); color: var(--water); }
.stat-icon-amber { background: rgba(169, 101, 53, 0.10); color: var(--amber); }

/* KEPT: action button color variants — complex gradients + composite shadows + hover effects */
.action-btn:active { transform: scale(0.98); }

.action-primary {
  border: 1px solid rgba(94, 123, 80, 0.28);
  background: linear-gradient(135deg, var(--leaf), #4a6e3e);
  color: #fffaf2;
  box-shadow:
    0 10px 26px rgba(67, 92, 60, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
}
.action-primary:hover {
  transform: translateY(-2px);
  box-shadow:
    0 16px 38px rgba(67, 92, 60, 0.24),
    0 0 22px rgba(201, 166, 70, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.20);
  filter: saturate(1.04);
}

.action-secondary {
  border: 1px solid rgba(62, 120, 145, 0.24);
  background: transparent;
  color: var(--water);
}
.action-secondary:hover {
  background: var(--turq-soft);
  border-color: rgba(62, 120, 145, 0.35);
  transform: translateY(-2px);
}

.action-danger {
  border: 1px solid rgba(198, 61, 66, 0.20);
  background: transparent;
  color: var(--carmine);
}
.action-danger:hover {
  background: var(--carmine-soft);
  border-color: rgba(198, 61, 66, 0.32);
  transform: translateY(-2px);
}

/* KEPT: clamp() values + transform */
.watermark {
  position: absolute;
  right: clamp(28px, 5vw, 72px);
  bottom: 5vh;
  color: rgba(32, 27, 22, 0.05);
  font-family: var(--font-sans);
  font-size: clamp(52px, 5.5vw, 106px);
  font-weight: 500;
  letter-spacing: 0.16em;
  transform: rotate(5deg);
  pointer-events: none;
}

/* KEPT: responsive overrides */
@media (max-width: 500px) {
  .cabinet { padding: 36px 28px 32px; }
  .stats-row { gap: 8px; }
  .stat-card { padding: 14px 8px; }
  .specimen { opacity: 0.16; width: clamp(64px, 18vw, 100px); }
  .watermark { display: none; }
  .deco-ring-inner { display: none; }
}
</style>
