/**
 * Симуляция СЛУЧАЙНЫХ ответов (без истинных профилей)
 * Показывает естественную наклонность опросника
 */

const questionWeights = {
  developer:     [0.86, 0.10, 0.10, 0.76, 0.67, 0.10, 0.05, 0.10, 0.19, 0.10],
  designer:      [0.12, 0.94, 0.12, 0.12, 0.12, 1.06, 0.06, 0.12, 0.12, 0.24],
  analyst:       [0.21, 0.21, 0.93, 0.10, 0.31, 0.10, 0.10, 0.83, 0.10, 0.10],
  manager:       [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 1.13, 0.45, 0.57, 0.17],
};

const NUM_STUDENTS = 5000;
const results = { developer: 0, designer: 0, analyst: 0, manager: 0 };
const scoreSums = { developer: 0, designer: 0, analyst: 0, manager: 0 };

for (let s = 0; s < NUM_STUDENTS; s++) {
  // Полностью случайные ответы 1-5
  const answers = Array.from({ length: 10 }, () => Math.floor(Math.random() * 5) + 1);
  
  const scores = { developer: 0, designer: 0, analyst: 0, manager: 0 };
  for (let i = 0; i < 10; i++) {
    for (const profile in questionWeights) {
      scores[profile] += answers[i] * questionWeights[profile][i];
    }
  }
  
  // Определяем профиль
  const predicted = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])[0][0];
  
  results[predicted]++;
  for (const p in scores) scoreSums[p] += scores[p];
}

console.log(`=== СЛУЧАЙНЫЕ ОТВЕТЫ: ${NUM_STUDENTS} "студентов" ===\n`);

console.log('Распределение результатов:');
for (const [profile, count] of Object.entries(results)) {
  const pct = (count / NUM_STUDENTS * 100).toFixed(1);
  console.log(`  ${profile.padEnd(10)}: ${count.toString().padStart(5)} (${pct}%)`);
}

console.log('\nСредние скоры (по всем):');
for (const [profile, sum] of Object.entries(scoreSums)) {
  console.log(`  ${profile.padEnd(10)}: ${(sum / NUM_STUDENTS).toFixed(2)}`);
}

// Проверка на доминирование
const maxCount = Math.max(...Object.values(results));
const dominant = Object.entries(results).find(([_, v]) => v === maxCount)[0];
if (maxCount > NUM_STUDENTS * 0.35) {
  console.log(`\n⚠️  ${dominant} доминирует (${maxCount}/${NUM_STUDENTS}) — есть системный перекос`);
} else {
  console.log(`\n✅ Системного доминирования нет`);
}