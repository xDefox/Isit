/**
 * Симулятор прохождения опроса 20 виртуальными студентами
 * Каждый студент имеет «истинный» профиль и отвечает с шумом
 */

// Веса из оpros.html (должны совпадать)
const questionWeights = {
  developer:     [0.9, 0.1, 0.1, 0.8, 0.7, 0.1, 0.05, 0.1, 0.2, 0.1],
  designer:      [0.1, 0.8, 0.1, 0.1, 0.1, 0.9, 0.05, 0.1, 0.1, 0.2],
  analyst:       [0.2, 0.2, 0.9, 0.1, 0.3, 0.1, 0.1, 0.8, 0.1, 0.1],
  manager:       [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 0.4, 0.5, 0.15],
};

// «Идеальные» ответы для каждого профиля (1-5)
const idealAnswers = {
  developer:     [5, 2, 2, 5, 5, 1, 1, 1, 5, 4],  // Q1, Q4, Q5, Q8, Q10 высоко
  designer:      [2, 5, 2, 2, 2, 5, 2, 2, 3, 3],  // Q2, Q6 высоко
  analyst:       [3, 3, 5, 2, 3, 2, 2, 5, 2, 2],  // Q3, Q8 высоко
  manager:       [2, 2, 3, 2, 2, 2, 5, 3, 4, 3],  // Q7 высоко
};

// Генерация ответов студента с шумом
function generateAnswers(trueProfile, noiseLevel = 1.2) {
  const ideal = idealAnswers[trueProfile];
  return ideal.map(v => {
    // Добавляем нормальный шум, клиппим к 1-5
    let noisy = v + (Math.random() - 0.5) * 2 * noiseLevel;
    noisy = Math.round(noisy);
    return Math.max(1, Math.min(5, noisy));
  });
}

// Расчёт скоров
function calculateScores(answers) {
  const scores = { developer: 0, designer: 0, analyst: 0, manager: 0 };
  for (let i = 0; i < answers.length; i++) {
    for (const profile in questionWeights) {
      scores[profile] += answers[i] * questionWeights[profile][i];
    }
  }
  return scores;
}

// Определение профиля
function determineProfile(scores) {
  return Object.entries(scores)
    .map(([profile, score]) => ({ profile, score }))
    .sort((a, b) => b.score - a.score)[0].profile;
}

// Создаём 100 студентов: по 25 на каждый истинный профиль
const profiles = ['developer', 'designer', 'analyst', 'manager'];
const students = [];

for (const trueProfile of profiles) {
  for (let i = 0; i < 25; i++) {
    students.push({
      id: `${trueProfile}_${i + 1}`,
      trueProfile,
      answers: generateAnswers(trueProfile),
    });
  }
}

// Запуск симуляции
console.log('=== СИМУЛЯЦИЯ 100 СТУДЕНТОВ ===\n');

const results = { developer: 0, designer: 0, analyst: 0, manager: 0 };
const details = [];

for (const s of students) {
  const scores = calculateScores(s.answers);
  const predicted = determineProfile(scores);
  const correct = predicted === s.trueProfile;
  results[predicted]++;
  details.push({ ...s, scores, predicted, correct });
  
  const status = correct ? '✓' : '✗';
  console.log(`${status} ${s.id.padEnd(16)} | true: ${s.trueProfile.padEnd(10)} | pred: ${predicted.padEnd(10)} | scores: ${JSON.stringify(scores)}`);
}

console.log('\n=== ИТОГОВАЯ РАСПРЕДЕЛЁННОСТЬ ===');
for (const [profile, count] of Object.entries(results)) {
  console.log(`${profile.padEnd(10)}: ${count} (${(count/students.length*100).toFixed(0)}%)`);
}

console.log('\n=== ТОЧНОСТЬ ПО ПРОФИЛЯМ ===');
for (const p of profiles) {
  const total = details.filter(d => d.trueProfile === p).length;
  const correct = details.filter(d => d.trueProfile === p && d.correct).length;
  console.log(`${p.padEnd(10)}: ${correct}/${total} = ${(correct/total*100).toFixed(0)}%`);
}

const overallAcc = details.filter(d => d.correct).length / details.length;
console.log(`\nОБЩАЯ ТОЧНОСТЬ: ${(overallAcc*100).toFixed(0)}%`);

// Проверка на доминирование
const maxCount = Math.max(...Object.values(results));
const dominant = Object.entries(results).find(([_, v]) => v === maxCount)[0];
if (maxCount > students.length * 0.4) {
  console.log(`\n⚠️  ВНИМАНИЕ: ${dominant} доминирует (${maxCount}/${students.length}) — нужно перебалансировать веса`);
} else {
  console.log(`\n✅ Распределение сбалансировано, доминирования нет`);
}