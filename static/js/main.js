// 获取DOM元素
const emotionForm = document.getElementById('emotion-form');
const eventInput = document.getElementById('event-input');
const recordsContainer = document.getElementById('records-container');

// 加载情绪记录列表
async function loadEmotionRecords() {
    try {
        const response = await fetch('/api/records');
        const result = await response.json();
        
        if (result.success) {
            displayRecords(result.data);
            // 更新问候语
            const greetingText = document.getElementById('greeting-text');
            greetingText.textContent = result.greeting;
        } else {
            console.error('加载记录失败:', result.error);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

// 显示情绪记录
function displayRecords(records) {
    recordsContainer.innerHTML = '';
    
    // 获取今天的开始时间（0点）和结束时间（23:59:59）
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // 过滤出今天的记录
    const todayRecords = records.filter(record => {
        const recordDate = new Date(record.fields.日期);
        return recordDate >= today && recordDate < tomorrow;
    });
    
    // 按时间倒序排序
    todayRecords.sort((a, b) => new Date(b.fields.日期) - new Date(a.fields.日期));
    
    if (todayRecords.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'empty-message';
        emptyMessage.textContent = '今天还没有记录~';
        recordsContainer.appendChild(emptyMessage);
        return;
    }
    
    todayRecords.forEach(record => {
        const recordElement = document.createElement('div');
        recordElement.className = 'record-item';
        
        const date = new Date(record.fields.日期);
        const formattedDate = date.toLocaleString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        recordElement.innerHTML = `
            <div class="record-date">${formattedDate}</div>
            <div class="record-content">${record.fields.事件}</div>
        `;
        
        recordsContainer.appendChild(recordElement);
    });
}

// 提交新的情绪记录
async function submitEmotionRecord(event) {
    event.preventDefault();
    
    const eventText = eventInput.value.trim();
    if (!eventText) return;
    
    try {
        const response = await fetch('/api/records', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: eventText
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            eventInput.value = '';
            loadEmotionRecords();
        } else {
            console.error('提交失败:', result.error);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

// 事件监听
emotionForm.addEventListener('submit', submitEmotionRecord);

// 页面加载时获取记录
document.addEventListener('DOMContentLoaded', loadEmotionRecords);