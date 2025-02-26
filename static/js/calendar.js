document.addEventListener('DOMContentLoaded', () => {
    const calendarGrid = document.getElementById('calendar-grid');

    // 计算日期范围
    function getDateRange() {
        const now = new Date();
        
        // 计算当前周的最后一天（周日）
        const endDate = new Date(now);
        const daysUntilSunday = 6 - endDate.getDay();
        endDate.setDate(endDate.getDate() + daysUntilSunday);
        endDate.setHours(23, 59, 59, 999);
        
        // 计算11周前的周一
        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - (11 * 7));
        // 确保从周一开始
        const daysToMonday = startDate.getDay() - 1;
        if (daysToMonday >= 0) {
            startDate.setDate(startDate.getDate() - daysToMonday);
        } else {
            startDate.setDate(startDate.getDate() - (7 + daysToMonday));
        }
        startDate.setHours(0, 0, 0, 0);
        
        return { startDate, endDate };
    }

    // 统计每天的情绪记录数量
    function countDailyRecords(records, startDate, endDate) {
        const dailyCounts = {};
        console.log('开始统计日期范围:', startDate.toLocaleString(), '至', endDate.toLocaleString());
        records.forEach(record => {
            const date = new Date(record.fields.日期);
            if (date >= startDate && date <= endDate) {
                const dateStr = date.toLocaleDateString('zh-CN');
                dailyCounts[dateStr] = (dailyCounts[dateStr] || 0) + 1;
                console.log('记录日期:', record.fields.日期, '分配到:', dateStr, '当前计数:', dailyCounts[dateStr]);
            }
        });
        console.log('最终统计结果:', dailyCounts);
        return dailyCounts;
    }

    // 渲染日历
    async function renderCalendar() {
        try {
            // 获取情绪记录数据
            const response = await fetch('/api/records');
            const data = await response.json();
            console.log('获取到的数据:', data);
            if (!data.success) throw new Error('获取数据失败');

            const { startDate, endDate } = getDateRange();
            const records = data.data;
            const emotionColors = data.emotion_colors;
            const dailyCounts = countDailyRecords(records, startDate, endDate);

            // 清空日历网格
            calendarGrid.innerHTML = '';

            // 创建12列，每列代表一周
            for (let col = 0; col < 12; col++) {
                const weekColumn = document.createElement('div');
                weekColumn.className = 'week-column';
                
                // 在每列中创建7天（周一到周日）
                for (let row = 0; row < 7; row++) {
                    const currentDate = new Date(startDate);
                    currentDate.setDate(startDate.getDate() + (col * 7) + row);
                    
                    const dateStr = currentDate.toLocaleDateString('zh-CN');
                    const count = dailyCounts[dateStr] || 0;
                    const displayCount = count > 5 ? '5+' : count.toString();

                    const dayElement = document.createElement('div');
                    dayElement.className = 'calendar-day';
                    dayElement.setAttribute('data-count', displayCount);
                    
                    // 获取当天UTC时间范围
                    const startOfDay = new Date(currentDate);
                    startOfDay.setUTCHours(0, 0, 0, 0);
                    const endOfDay = new Date(currentDate);
                    endOfDay.setUTCHours(24, 0, 0, 0);

                    // 查找当天时间范围内的情绪颜色
                    const dayEmotionColor = Object.entries(emotionColors).find(([timestamp]) => {
                        const recordTime = parseInt(timestamp);
                        return recordTime >= startOfDay.getTime() && recordTime < endOfDay.getTime();
                    });

                    if (dayEmotionColor) {
                        weekColumn.appendChild(dayElement);
                        // 使用requestAnimationFrame确保在下一帧渲染时获取元素宽度
                        requestAnimationFrame(() => {
                            const elementWidth = dayElement.offsetWidth;
                            console.log(`元素 ${dateStr} 的宽度为 ${elementWidth} 像素`);
                            const borderWidth = Math.max(elementWidth * 0.2, 2);
                            dayElement.style.boxShadow = `inset 0 0 0 ${borderWidth}px ${dayEmotionColor[1]}`;
                        });
                    } else {
                        weekColumn.appendChild(dayElement);
                    }
                    
                    dayElement.setAttribute('title', `${dateStr}: ${count}次记录`);
                    // 移除这行，因为我们已经在上面添加了元素
                    // weekColumn.appendChild(dayElement);
                }
                
                calendarGrid.appendChild(weekColumn);
            }

            // 添加星期标识列
            const weekdayLabels = document.createElement('div');
            weekdayLabels.className = 'weekday-labels';
            const weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
            weekdays.forEach(day => {
                const label = document.createElement('div');
                label.className = 'weekday-label';
                label.textContent = day;
                weekdayLabels.appendChild(label);
            });
            calendarGrid.appendChild(weekdayLabels);

        } catch (error) {
            console.error('渲染日历失败:', error);
        }
    }

    // 初始渲染
    renderCalendar();
});