//Navigation Section
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})


//Menstrual Phase Cycle chart
document.addEventListener("DOMContentLoaded", function () {
    // Check if the page belongs to the "Next Cycle" section
    if (document.body.classList.contains('next_cycle')) {
        const chartCanvas = document.getElementById('menstrualCycleChart');
        
        // Ensure the canvas element exists before proceeding
        if (chartCanvas) {
            const ctx = chartCanvas.getContext('2d');

            // Data for the chart
            const data = {
                labels: [
                    'Early Follicular Phase',
                    'Late Follicular Phase',
                    'Ovulation',
                    'Early Luteal Phase',
                    'Late Luteal Phase'
                ],
                datasets: [{
                    data: [5, 9, 1, 7, 6], // Duration of each phase in days
                    backgroundColor: [
                        '#FFE699', // Light yellow for early follicular
                        '#FFD966', // Dark yellow for late follicular
                        '#B6D7A8', // Green for ovulation
                        '#F4CCCC', // Light red for early luteal
                        '#E06666'  // Red for late luteal
                    ],
                    hoverOffset: 4
                }]
            };

            // Configuration for the chart
            const config = {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function (tooltipItem) {
                                    const phase = data.labels[tooltipItem.dataIndex];
                                    const days = data.datasets[0].data[tooltipItem.dataIndex];
                                    return `${phase}: ${days} days`;
                                }
                            }
                        }
                    },
                    cutout: '50%' // Makes the chart look like a ring
                }
            };

            // Render the chart
            new Chart(ctx, config);
        }
    }
});
