// Global chart instances
let sentimentChart;
let keywordChart;
let trendChart;
let sourceChart;

// Chart color schemes
const chartColors = {
  positive: 'rgba(40, 167, 69, 0.8)',
  negative: 'rgba(220, 53, 69, 0.8)',
  neutral: 'rgba(255, 193, 7, 0.8)',
  default: [
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 99, 132, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 205, 86, 0.8)',
    'rgba(201, 203, 207, 0.8)',
    'rgba(138, 43, 226, 0.8)',
    'rgba(0, 128, 128, 0.8)',
    'rgba(220, 20, 60, 0.8)'
  ]
};

// Chart options
const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    }
  }
};

// ========= UTILITY FUNCTIONS =========

// Format date for display
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return moment(dateString).format('MMM D, YYYY h:mm A');
}

// Get filter values
function getFilters() {
  return {
    days: $('#timeFilter').val(),
    sentiment: $('#sentimentFilter').val(),
    interval: $('#intervalFilter').val()
  };
}

// Update the last updated timestamp
function updateLastUpdated() {
  $('#lastUpdated span').text(moment().format('MMM D, YYYY h:mm:ss A'));
}

// Simple error handler for fetch requests
async function fetchWithErrorHandling(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
}

// Build query string from filters
function buildQueryString(filters = {}) {
  return Object.entries(filters)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');
}

// Create a chart if it doesn't exist, otherwise update it
function createOrUpdateChart(chartInstance, config) {
  if (chartInstance) {
    chartInstance.data = config.data;
    chartInstance.options = config.options;
    chartInstance.update();
    return chartInstance;
  } else {
    return new Chart(config.ctx, {
      type: config.type,
      data: config.data,
      options: config.options
    });
  }
}

// ========= DATA FETCHING FUNCTIONS =========

// Fetch and display overall stats
async function fetchStats() {
  const data = await fetchWithErrorHandling('/api/stats');
  if (!data) return;
  
  const stats = JSON.parse(data);
  
  // Process sentiment counts for stats cards
  const sentimentMap = {};
  stats.sentiment_counts.forEach(item => {
    sentimentMap[item._id] = item.count;
  });
  
  const total = stats.total || 0;
  const positive = sentimentMap.positive || 0;
  const negative = sentimentMap.negative || 0;
  const neutral = sentimentMap.neutral || 0;
  
  // Calculate percentages
  const positivePercent = total > 0 ? Math.round((positive / total) * 100) : 0;
  const negativePercent = total > 0 ? Math.round((negative / total) * 100) : 0;
  const neutralPercent = total > 0 ? Math.round((neutral / total) * 100) : 0;
  
  // Update stats row
  $('#statsRow').html(`
    <div class="col-md-3">
      <div class="card stat-card">
        <div class="stat-value">${total.toLocaleString()}</div>
        <div class="stat-label">TOTAL REVIEWS</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card stat-card">
        <div class="stat-value sentiment-positive">${positivePercent}%</div>
        <div class="stat-label">POSITIVE SENTIMENT</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card stat-card">
        <div class="stat-value sentiment-negative">${negativePercent}%</div>
        <div class="stat-label">NEGATIVE SENTIMENT</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card stat-card">
        <div class="stat-value sentiment-neutral">${neutralPercent}%</div>
        <div class="stat-label">NEUTRAL SENTIMENT</div>
      </div>
    </div>
  `);
  
  // Update last review time
  if (stats.latest_timestamp) {
    $('#lastUpdated span').text(formatDate(stats.latest_timestamp));
  }

  return stats;
}

// Fetch and display sentiment distribution
async function fetchSentimentCounts() {
  const filters = getFilters();
  const queryString = buildQueryString({ days: filters.days });
  const url = `/api/sentiment_counts${queryString ? '?' + queryString : ''}`;
  
  const data = await fetchWithErrorHandling(url);
  if (!data) return;
  
  // Process data
  const labels = [];
  const counts = [];
  const backgroundColors = [];
  
  // Sort by sentiment for consistent ordering
  const sortOrder = { 'positive': 0, 'neutral': 1, 'negative': 2 };
  data.sort((a, b) => sortOrder[a._id] - sortOrder[b._id]);
  
  data.forEach(item => {
    labels.push(item._id || 'Unknown');
    counts.push(item.count);
    backgroundColors.push(chartColors[item._id] || chartColors.default[0]);
  });
  
  // Update total count badge
  const total = counts.reduce((acc, count) => acc + count, 0);
  $('#sentimentTotal').text(`Total: ${total.toLocaleString()}`);
  
  // Create or update chart
  sentimentChart = createOrUpdateChart(sentimentChart, {
    ctx: document.getElementById('sentimentChart'),
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: backgroundColors,
        borderWidth: 1
      }]
    },
    options: {
      ...defaultOptions,
      plugins: {
        ...defaultOptions.plugins,
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
  
  return data;
}

// Fetch and display top keywords
async function fetchTopKeywords() {
  const filters = getFilters();
  const queryString = buildQueryString({ 
    days: filters.days,
    sentiment: filters.sentiment 
  });
  const url = `/api/top_keywords${queryString ? '?' + queryString : ''}`;
  
  const data = await fetchWithErrorHandling(url);
  if (!data) return;
  
  // Process data
  const labels = data.map(d => d._id || 'N/A');
  const counts = data.map(d => d.count);
  
  // Create or update chart
  keywordChart = createOrUpdateChart(keywordChart, {
    ctx: document.getElementById('keywordChart'),
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Keyword Frequency',
        data: counts,
        backgroundColor: chartColors.default,
        borderWidth: 1
      }]
    },
    options: {
      ...defaultOptions,
      indexAxis: 'y',
      plugins: {
        ...defaultOptions.plugins,
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Frequency'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Keywords'
          }
        }
      }
    }
  });
  
  return data;
}

// Fetch and display sentiment over time
async function fetchSentimentOverTime() {
  const filters = getFilters();
  const queryString = buildQueryString({ 
    days: filters.days || 30,
    interval: filters.interval || 'day'
  });
  const url = `/api/sentiment_over_time${queryString ? '?' + queryString : ''}`;
  
  const data = await fetchWithErrorHandling(url);
  if (!data) return;
  
  // Process data for time series
  const timeLabels = new Set();
  const sentimentTypes = new Set();
  const dataMap = {};
  
  // First pass: collect all unique dates and sentiment types
  data.forEach(item => {
    const date = item._id.date;
    const sentiment = item._id.sentiment;
    
    timeLabels.add(date);
    sentimentTypes.add(sentiment);
    
    if (!dataMap[sentiment]) {
      dataMap[sentiment] = {};
    }
    dataMap[sentiment][date] = item.count;
  });
  
  // Sort time labels
  const sortedTimeLabels = Array.from(timeLabels).sort();
  
  // Format labels based on interval
  const formattedLabels = sortedTimeLabels.map(label => {
    if (filters.interval === 'month') {
      return moment(label, 'YYYY-MM').format('MMM YYYY');
    } else if (filters.interval === 'week') {
      return `Week ${label.split('-')[1]}, ${label.split('-')[0]}`;
    } else {
      return moment(label).format('MMM D');
    }
  });
  
  // Create datasets
  const datasets = [];
  const sentimentOrder = ['positive', 'neutral', 'negative'];
  
  // Sort sentiment types based on predetermined order
  const sortedSentimentTypes = Array.from(sentimentTypes).sort((a, b) => {
    return sentimentOrder.indexOf(a) - sentimentOrder.indexOf(b);
  });
  
  sortedSentimentTypes.forEach(sentiment => {
    const data = sortedTimeLabels.map(date => dataMap[sentiment][date] || 0);
    
    datasets.push({
      label: sentiment.charAt(0).toUpperCase() + sentiment.slice(1),
      data: data,
      backgroundColor: chartColors[sentiment] || chartColors.default[0],
      borderColor: chartColors[sentiment] || chartColors.default[0],
      tension: 0.3,
      fill: false
    });
  });
  
  // Create or update chart
  trendChart = createOrUpdateChart(trendChart, {
    ctx: document.getElementById('sentimentTrendChart'),
    type: 'line',
    data: {
      labels: formattedLabels,
      datasets: datasets
    },
    options: {
      ...defaultOptions,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Reviews'
          }
        }
      }
    }
  });
  
  return data;
}

// Fetch and display sentiment by source
async function fetchSentimentBySource() {
  const data = await fetchWithErrorHandling('/api/sentiment_by_source');
  if (!data) return;
  
  // Process data
  const sources = new Set();
  const dataMap = {};
  
  // First pass: collect all unique sources
  data.forEach(item => {
    const source = item._id.source || 'Unknown';
    sources.add(source);
    
    if (!dataMap[source]) {
      dataMap[source] = {
        positive: 0,
        negative: 0,
        neutral: 0
      };
    }
    
    const sentiment = item._id.sentiment;
    if (sentiment) {
      dataMap[source][sentiment] = item.count;
    }
  });
  
  const labels = Array.from(sources);
  
  // Create datasets for each sentiment
  const positiveData = labels.map(source => dataMap[source].positive || 0);
  const negativeData = labels.map(source => dataMap[source].negative || 0);
  const neutralData = labels.map(source => dataMap[source].neutral || 0);
  
  // Create or update chart
  sourceChart = createOrUpdateChart(sourceChart, {
    ctx: document.getElementById('sourceChart'),
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Positive',
          data: positiveData,
          backgroundColor: chartColors.positive,
          stack: 'Stack 0'
        },
        {
          label: 'Neutral',
          data: neutralData,
          backgroundColor: chartColors.neutral,
          stack: 'Stack 0'
        },
        {
          label: 'Negative',
          data: negativeData,
          backgroundColor: chartColors.negative,
          stack: 'Stack 0'
        }
      ]
    },
    options: {
      ...defaultOptions,
      scales: {
        x: {
          stacked: true,
          title: {
            display: true,
            text: 'Source'
          }
        },
        y: {
          stacked: true,
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Reviews'
          }
        }
      }
    }
  });
  
  return data;
}

// Fetch and display recent reviews
async function fetchRecentReviews() {
  const reviewSentiment = $('#reviewSentimentFilter').val();
  const queryString = buildQueryString({ 
    sentiment: reviewSentiment,
    limit: 10
  });
  const url = `/api/recent_reviews${queryString ? '?' + queryString : ''}`;
  
  const data = await fetchWithErrorHandling(url);
  if (!data) return;
  
  const reviews = JSON.parse(data);
  const list = document.getElementById('reviewList');
  list.innerHTML = '';
  
  // If no reviews, show a message
  if (reviews.length === 0) {
    list.innerHTML = '<div class="text-center p-4 text-muted">No reviews found matching the selected criteria.</div>';
    return;
  }
  
  // Display reviews
  reviews.forEach(doc => {
    const sentimentClass = doc.sentiment || 'neutral';
    const date = formatDate(doc.timestamp);
    const source = doc.source || 'Unknown';
    
    const li = document.createElement('div');
    li.className = `review-item ${sentimentClass}`;
    li.innerHTML = `
      <div class="review-meta">
        <span class="badge bg-secondary">${source}</span>
        <span class="badge bg-${getSentimentBadgeColor(sentimentClass)}">${sentimentClass.toUpperCase()}</span> 
        <span class="text-muted ms-2">${date}</span>
      </div>
      <div class="review-text mt-2">${doc.text || 'No content'}</div>
    `;
    list.appendChild(li);
  });
  
  return reviews;
}

// Helper function to get badge color based on sentiment
function getSentimentBadgeColor(sentiment) {
  const colorMap = {
    'positive': 'success',
    'negative': 'danger',
    'neutral': 'warning'
  };
  return colorMap[sentiment] || 'secondary';
}

// ========= MAIN FUNCTIONS =========

// Load all charts and data
async function loadAllData() {
  // Show loading indicators
  $('.card-body').addClass('loading');
  
  try {
    // Fetch data concurrently
    await Promise.all([
      fetchStats(),
      fetchSentimentCounts(),
      fetchTopKeywords(),
      fetchSentimentOverTime(),
      fetchSentimentBySource(),
      fetchRecentReviews()
    ]);
    
    // Update timestamp
    updateLastUpdated();
  } catch (error) {
    console.error('Error loading data:', error);
  //  alert('There was an error loading the dashboard data. Please try again.');
  } finally {
    // Hide loading indicators
    $('.card-body').removeClass('loading');
  }
}

// ========= EVENT HANDLERS =========

// Set up event listeners
function setupEventListeners() {
  // Refresh button
  $('#refreshBtn').on('click', function() {
    loadAllData();
  });
  
  // Filter change events
  $('#timeFilter, #sentimentFilter, #intervalFilter').on('change', function() {
    loadAllData();
  });
  
  // Review sentiment filter
  $('#reviewSentimentFilter').on('change', function() {
    fetchRecentReviews();
  });
}

// Document ready
$(document).ready(function() {
  // Set up event listeners
  setupEventListeners();
  
  // Initial data load
  loadAllData();
  
  // Auto-refresh every 60 seconds
  setInterval(loadAllData, 60000);
});