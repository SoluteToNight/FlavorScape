<template>
  <main class="home-cover">
    <section class="cover-stage" aria-label="寻味地理首页">
      <img class="cover-map" src="/home/cover-map.png" alt="" />
      <div class="cover-wash"></div>

      <div class="hero-copy">
        <div class="title-block">
          <h1 class="hero-title">
            <span class="title-green">寻味</span>
            <span class="title-red">地理</span>
          </h1>
          <div class="english-mark">
            <span>FLAVOR ATLAS</span>
            <span>OF CHINA <i>味</i></span>
          </div>
        </div>

        <p class="hero-slogan">把地方风味写成一部可漫游的地理志</p>

        <div class="capability-row" aria-label="核心能力">
          <button
            v-for="item in capabilities"
            :key="item.title"
            class="capability-item"
            type="button"
            @click="router.push(item.path)"
          >
            <span class="capability-icon" v-html="item.icon"></span>
            <span class="capability-title">{{ item.title }}</span>
            <span class="capability-desc">{{ item.desc }}</span>
          </button>
        </div>

        <div class="hero-actions" aria-label="首页操作">
          <button class="primary-action" type="button" @click="router.push('/map')">
            <span>开始寻味之旅</span>
            <span class="action-icon">→</span>
          </button>
          <button class="secondary-action" type="button" @click="router.push('/map')">
            <span>探索风味地图</span>
            <span class="play-dot">▷</span>
          </button>
        </div>
      </div>

    </section>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const pinIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-5.2 7-12a7 7 0 0 0-14 0c0 6.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/></svg>`
const leafIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19c8.5 0 13-5.6 14-14-8.4 1-14 5.5-14 14Z"/><path d="M5 19 17 7"/><path d="M9 8c0 2.5 1.2 4.6 3.2 6"/><path d="M8 14c2.1.2 4.2 1 5.9 2.4"/></svg>`
const routeIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6c2.8-2.2 5.4-2.2 8 0s5.2 2.2 8 0"/><path d="M4 18c2.8-2.2 5.4-2.2 8 0s5.2 2.2 8 0"/><circle cx="5" cy="6" r="1.7"/><circle cx="19" cy="18" r="1.7"/></svg>`
const bookIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 5.5A3 3 0 0 1 7.5 3H20v16H7.5a3 3 0 0 0-3 3V5.5Z"/><path d="M4.5 5.5A3 3 0 0 1 7.5 8H20"/><path d="M9 12h6"/><path d="M9 15h4"/></svg>`
const capabilities = [
  { title: '食材溯源', desc: '追溯风味根脉', path: '/spread', icon: pinIcon },
  { title: '工艺文明', desc: '解码匠心技艺', path: '/archive', icon: leafIcon },
  { title: '路线迁徙', desc: '重现风味流动', path: '/map', icon: routeIcon },
  { title: '品牌叙事', desc: '讲述风味故事', path: '/marketing', icon: bookIcon },
]

</script>

<style scoped>
.home-cover {
  min-height: 100vh;
  background: #f4efe6;
  color: #302b22;
  font-family: var(--font-sans);
  overflow: hidden;
}

.cover-stage {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  isolation: isolate;
}

.cover-map {
  position: absolute;
  inset: 0;
  z-index: -3;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 26px;
  filter: saturate(0.98) contrast(1.01);
}

.cover-wash {
  position: absolute;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(246, 241, 232, 0.34) 0%, rgba(246, 241, 232, 0.14) 34%, rgba(246, 241, 232, 0) 62%),
    linear-gradient(180deg, rgba(246, 241, 232, 0.2) 0%, rgba(246, 241, 232, 0) 26%, rgba(232, 224, 210, 0.16) 100%);
}

.hero-copy {
  position: absolute;
  left: var(--hero-offset-x);
  top: max(calc(var(--navbar-h) + 61px), calc(var(--hero-offset-y) + 25px));
  z-index: 2;
  width: var(--hero-copy-w);
}

.title-block {
  position: relative;
  width: clamp(420px, 32vw, 520px);
}

.hero-title {
  display: flex;
  flex-direction: column;
  margin: 0;
  font-family: var(--font-serif), STSong, serif;
  font-size: clamp(112px, 8.8vw, 142px);
  font-weight: 800;
  line-height: 0.92;
  letter-spacing: 0;
}

.title-green {
  color: #3d4b2c;
}

.title-red {
  margin-left: clamp(54px, 4.3vw, 74px);
  margin-top: 2px;
  color: #a2482a;
}

.english-mark {
  position: absolute;
  left: clamp(258px, 20vw, 330px);
  top: clamp(72px, 6.4vw, 92px);
  display: grid;
  gap: 2px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(13px, 1vw, 16px);
  line-height: 1.35;
  letter-spacing: 0;
  color: #6d624e;
}

.english-mark i {
  display: inline-grid;
  width: 18px;
  height: 18px;
  margin-left: 6px;
  place-items: center;
  background: #a2482a;
  color: #fff8eb;
  font-family: var(--font-serif);
  font-size: 11px;
  font-style: normal;
  line-height: 1;
}

.hero-slogan {
  margin-top: clamp(20px, 2.3vh, 32px);
  font-family: var(--font-serif), STSong, serif;
  font-size: clamp(21px, 1.6vw, 25px);
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0;
  color: #3f4531;
}

.capability-row {
  display: flex;
  gap: clamp(18px, 2vw, 34px);
  margin-top: clamp(18px, 2.2vh, 30px);
  width: min(100%, 560px);
}

.capability-item {
  display: grid;
  justify-items: center;
  gap: 7px;
  width: 112px;
  border: 0;
  background: transparent;
  color: #465236;
  cursor: pointer;
  font: inherit;
}

.capability-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid rgba(58, 73, 42, 0.62);
  border-radius: 50%;
  background: rgba(249, 245, 236, 0.34);
}

.capability-icon svg {
  width: 22px;
  height: 22px;
}

.capability-title {
  font-family: var(--font-serif), STSong, serif;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 0;
  color: #343225;
}

.capability-desc {
  font-size: 12px;
  font-weight: 400;
  line-height: 1.25;
  letter-spacing: 0;
  color: #7e7564;
  white-space: nowrap;
}

.hero-actions {
  display: flex;
  gap: clamp(14px, 1.4vw, 20px);
  margin-top: clamp(24px, 3vh, 42px);
}

.primary-action,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  border-radius: 8px;
  font-family: var(--font-serif), STSong, serif;
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0;
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.primary-action {
  gap: 28px;
  min-width: 204px;
  padding: 0 28px 0 34px;
  border: 1px solid rgba(134, 54, 26, 0.22);
  background: linear-gradient(180deg, #bd5a34 0%, #9f3f20 100%);
  color: #fff8ec;
  box-shadow: 0 15px 28px rgba(126, 55, 25, 0.24);
}

.secondary-action {
  gap: 14px;
  min-width: 184px;
  padding: 0 26px;
  border: 1px solid rgba(105, 87, 59, 0.28);
  background: rgba(249, 246, 238, 0.56);
  color: #3c3529;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.primary-action:hover,
.secondary-action:hover {
  transform: translateY(-2px);
}

.primary-action:hover {
  box-shadow: 0 18px 34px rgba(126, 55, 25, 0.3);
}

.secondary-action:hover {
  background: rgba(255, 251, 243, 0.72);
}

.action-icon {
  font-size: 24px;
  line-height: 1;
}

.play-dot {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border: 1px solid rgba(84, 74, 52, 0.48);
  border-radius: 50%;
  font-size: 10px;
  line-height: 1;
}

@media (max-width: 1439px), (max-height: 800px) {
  .hero-copy {
    width: min(560px, calc(100vw - 96px));
  }

  .hero-copy,
  .title-block {
    max-width: 100%;
  }

  .capability-item {
    width: 96px;
  }

  .primary-action,
  .secondary-action {
    height: 52px;
  }
}

@media (max-height: 760px) {
  .capability-desc {
    font-size: 11px;
  }
}
</style>
