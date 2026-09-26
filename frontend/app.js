/* =========================================================
   THREATX — FRONTEND DASHBOARD
   ========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";

const LIVE_REFRESH_INTERVAL = 3000;

let liveRefreshTimer = null;


/* =========================================================
   DOM READY
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    console.log("ThreatX frontend loaded.");

    loadDashboard();

    loadSimulationStatus();

    startLiveRefresh();


    /* =====================================================
       REFRESH BUTTON
       ===================================================== */

    const refreshButton =
        document.getElementById("refreshButton");


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            () => {

                loadDashboard();
                loadSimulationStatus();

            }
        );

    }


    /* =====================================================
       SIMULATION BUTTONS
       ===================================================== */

    const startSimulationButton =
        document.getElementById(
            "startSimulationButton"
        );


    const stopSimulationButton =
        document.getElementById(
            "stopSimulationButton"
        );


    if (startSimulationButton) {

        startSimulationButton.addEventListener(
            "click",
            startMonitoring
        );

    }


    if (stopSimulationButton) {

        stopSimulationButton.addEventListener(
            "click",
            stopMonitoring
        );

    }

});


/* =========================================================
   LOAD COMPLETE DASHBOARD
   ========================================================= */

async function loadDashboard() {

    console.log(
        "Loading ThreatX dashboard..."
    );


    try {

        await Promise.all([
            loadStatistics(),
            loadAlerts(),
            loadTraffic(),
            loadAnalytics()
        ]);


        console.log(
            "ThreatX dashboard loaded successfully."
        );


    } catch (error) {

        console.error(
            "Failed to load ThreatX dashboard:",
            error
        );

    }

}


/* =========================================================
   LOAD STATISTICS
   ========================================================= */

async function loadStatistics() {

    console.log(
        "Requesting /api/statistics..."
    );


    const response =
        await fetch(
            `${API_BASE_URL}/api/statistics`
        );


    console.log(
        "Statistics HTTP status:",
        response.status
    );


    if (!response.ok) {

        throw new Error(
            `Statistics API returned ${response.status}`
        );

    }


    const data =
        await response.json();


    console.log(
        "Statistics received:",
        data
    );


    /* =====================================================
       MAIN STATISTICS CARDS
       ===================================================== */

    setText(
        "totalTraffic",
        data.total_traffic
    );


    setText(
        "attackTraffic",
        data.attack_traffic
    );


    setText(
        "normalTraffic",
        data.normal_traffic
    );


    setText(
        "criticalAlerts",
        data.critical_alerts
    );


    /* =====================================================
       SEVERITY SUMMARY
       ===================================================== */

    setText(
        "criticalCount",
        data.critical_alerts
    );


    setText(
        "highCount",
        data.high_alerts
    );


    setText(
        "mediumCount",
        data.medium_alerts
    );


    setText(
        "lowCount",
        data.low_alerts
    );


    /* =====================================================
       ANALYTICS OVERVIEW
       ===================================================== */

    const normalPercentage =
        Number(
            data.normal_percentage || 0
        );


    const attackPercentage =
        Number(
            data.attack_percentage || 0
        );


    const totalAlerts =
        Number(
            data.total_alerts || 0
        );


    const highCriticalAlerts =
        Number(
            data.high_alerts || 0
        ) +
        Number(
            data.critical_alerts || 0
        );


    setText(
        "normalPercentage",
        `${normalPercentage}%`
    );


    setText(
        "attackPercentage",
        `${attackPercentage}%`
    );


    setText(
        "totalAlerts",
        totalAlerts
    );


    setText(
        "highCriticalAlerts",
        highCriticalAlerts
    );


    /* =====================================================
       ANALYTICS PROGRESS BARS
       ===================================================== */

    const normalProgress =
        document.getElementById(
            "normalProgress"
        );


    const attackProgress =
        document.getElementById(
            "attackProgress"
        );


    if (normalProgress) {

        normalProgress.style.width =
            `${normalPercentage}%`;

    }


    if (attackProgress) {

        attackProgress.style.width =
            `${attackPercentage}%`;

    }


    /* =====================================================
       ATTACK DISTRIBUTION
       ===================================================== */

    renderAttackDistribution(
        data.attack_distribution
    );

}


/* =========================================================
   ATTACK DISTRIBUTION
   ========================================================= */

function renderAttackDistribution(distribution) {

    const container =
        document.getElementById(
            "attackDistributionChart"
        );


    if (!container) {

        console.warn(
            "#attackDistributionChart was not found."
        );

        return;

    }


    container.innerHTML = "";


    const entries =
        Object.entries(
            distribution || {}
        );


    /* =====================================================
       EMPTY DATA
       ===================================================== */

    if (entries.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No attacks detected yet.
            </div>
        `;

        return;

    }


    /* =====================================================
       FIND MAX VALUE
       ===================================================== */

    const maxValue =
        Math.max(
            ...entries.map(
                ([, value]) =>
                    Number(value)
            ),
            1
        );


    /* =====================================================
       CREATE BARS
       ===================================================== */

    entries.forEach(
        ([category, count]) => {

            const numericCount =
                Number(count);


            const percentage =
                maxValue > 0
                    ? (numericCount / maxValue) * 100
                    : 0;


            const item =
                document.createElement("div");


            item.className =
                "attack-bar-item";


            item.innerHTML = `

                <div class="attack-bar-header">

                    <span class="attack-category">
                        ${escapeHtml(category)}
                    </span>

                    <strong>
                        ${numericCount}
                    </strong>

                </div>


                <div class="attack-bar-track">

                    <div
                        class="attack-bar-fill"
                        style="width: ${percentage}%;">
                    </div>

                </div>

            `;


            container.appendChild(item);

        }
    );

}


/* =========================================================
   LOAD ALERTS
   ========================================================= */

async function loadAlerts() {

    console.log(
        "Requesting /api/alerts..."
    );


    const response =
        await fetch(
            `${API_BASE_URL}/api/alerts`
        );


    console.log(
        "Alerts HTTP status:",
        response.status
    );


    if (!response.ok) {

        throw new Error(
            `Alerts API returned ${response.status}`
        );

    }


    const alerts =
        await response.json();


    console.log(
        "Alerts received:",
        alerts
    );


    renderAlerts(alerts);

}


/* =========================================================
   LOAD TRAFFIC
   ========================================================= */

async function loadTraffic() {

    console.log(
        "Requesting /api/traffic..."
    );


    const response =
        await fetch(
            `${API_BASE_URL}/api/traffic`
        );


    console.log(
        "Traffic HTTP status:",
        response.status
    );


    if (!response.ok) {

        throw new Error(
            `Traffic API returned ${response.status}`
        );

    }


    const traffic =
        await response.json();


    console.log(
        "Traffic received:",
        traffic
    );


    renderTraffic(traffic);

}


/* =========================================================
   LOAD TIME-SERIES ANALYTICS
   ========================================================= */

async function loadAnalytics() {

    console.log(
        "Requesting /api/analytics..."
    );


    const response =
        await fetch(
            `${API_BASE_URL}/api/analytics`
        );


    console.log(
        "Analytics HTTP status:",
        response.status
    );


    if (!response.ok) {

        throw new Error(
            `Analytics API returned ${response.status}`
        );

    }


    const data =
        await response.json();


    console.log(
        "Analytics received:",
        data
    );


    /* =====================================================
       TRAFFIC TIMELINE
       ===================================================== */

    renderTrafficTimeline(
        data.timeline
    );


    /* =====================================================
       THREAT ACTIVITY TIMELINE
       ===================================================== */

    renderThreatActivity(
        data.attack_timeline
    );

}


/* =========================================================
   TRAFFIC TIMELINE
   ========================================================= */

function renderTrafficTimeline(timeline) {

    const container =
        document.getElementById(
            "trafficTimelineChart"
        );


    const maxValueElement =
        document.getElementById(
            "chartMaxValue"
        );


    if (!container) {

        console.warn(
            "#trafficTimelineChart was not found."
        );

        return;

    }


    container.innerHTML = "";


    if (
        !timeline ||
        timeline.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No traffic activity available yet.
            </div>
        `;


        if (maxValueElement) {

            maxValueElement.textContent = "0";

        }


        return;

    }


    /* =====================================================
       FIND MAXIMUM
       ===================================================== */

    const maxValue =
        Math.max(
            ...timeline.map(item =>
                Math.max(
                    Number(item.normal || 0),
                    Number(item.attack || 0),
                    Number(item.alerts || 0)
                )
            ),
            1
        );


    if (maxValueElement) {

        maxValueElement.textContent =
            maxValue;

    }


    /* =====================================================
       CREATE COLUMNS
       ===================================================== */

    timeline.forEach(
        item => {

            const column =
                document.createElement(
                    "div"
                );


            column.className =
                "timeline-column";


            const bars =
                document.createElement(
                    "div"
                );


            bars.className =
                "timeline-bars";


            /* =================================================
               NORMAL
               ================================================= */

            const normalBar =
                document.createElement(
                    "div"
                );


            normalBar.className =
                "timeline-bar timeline-normal";


            normalBar.style.height =
                `${getChartHeight(
                    item.normal,
                    maxValue
                )}%`;


            normalBar.title =
                `Normal: ${item.normal}`;


            /* =================================================
               ATTACK
               ================================================= */

            const attackBar =
                document.createElement(
                    "div"
                );


            attackBar.className =
                "timeline-bar timeline-attack";


            attackBar.style.height =
                `${getChartHeight(
                    item.attack,
                    maxValue
                )}%`;


            attackBar.title =
                `Attacks: ${item.attack}`;


            /* =================================================
               ALERT
               ================================================= */

            const alertBar =
                document.createElement(
                    "div"
                );


            alertBar.className =
                "timeline-bar timeline-alert";


            alertBar.style.height =
                `${getChartHeight(
                    item.alerts,
                    maxValue
                )}%`;


            alertBar.title =
                `Alerts: ${item.alerts}`;


            /* =================================================
               TIME LABEL
               ================================================= */

            const timeLabel =
                document.createElement(
                    "span"
                );


            timeLabel.className =
                "timeline-time";


            timeLabel.textContent =
                formatChartTime(
                    item.timestamp
                );


            /* =================================================
               APPEND
               ================================================= */

            bars.appendChild(
                normalBar
            );


            bars.appendChild(
                attackBar
            );


            bars.appendChild(
                alertBar
            );


            column.appendChild(
                bars
            );


            column.appendChild(
                timeLabel
            );


            container.appendChild(
                column
            );

        }
    );

}


/* =========================================================
   CHART HEIGHT
   ========================================================= */

function getChartHeight(
    value,
    maxValue
) {

    const numericValue =
        Number(value || 0);


    if (numericValue <= 0) {

        return 2;

    }


    return Math.max(
        3,
        (numericValue / maxValue) * 100
    );

}


/* =========================================================
   CHART TIME FORMAT
   ========================================================= */

function formatChartTime(timestamp) {

    if (!timestamp) {

        return "-";

    }


    const date =
        new Date(timestamp);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "-";

    }


    return date.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* =========================================================
   THREAT ACTIVITY TIMELINE
   ========================================================= */

function renderThreatActivity(timeline) {

    const container =
        document.getElementById(
            "threatActivityTimeline"
        );


    if (!container) {

        console.warn(
            "#threatActivityTimeline was not found."
        );

        return;

    }


    container.innerHTML = "";


    if (
        !timeline ||
        timeline.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No threat activity available yet.
            </div>
        `;

        return;

    }


    /* =====================================================
       FIND MAXIMUM TOTAL ATTACKS
       ===================================================== */

    let maxValue = 1;


    timeline.forEach(
        item => {

            const categories =
                item.categories || {};


            const total =
                Object.values(
                    categories
                ).reduce(
                    (
                        sum,
                        value
                    ) =>
                        sum +
                        Number(value || 0),
                    0
                );


            maxValue =
                Math.max(
                    maxValue,
                    total
                );

        }
    );


    /* =====================================================
       CREATE TIMELINE COLUMNS
       ===================================================== */

    timeline.forEach(
        item => {

            const column =
                document.createElement(
                    "div"
                );


            column.className =
                "threat-time-column";


            const stack =
                document.createElement(
                    "div"
                );


            stack.className =
                "threat-stack";


            const categories =
                item.categories || {};


            const categoryOrder = [

                "Generic",

                "Exploits",

                "DoS",

                "Fuzzers"

            ];


            let knownTotal = 0;


            /* =================================================
               KNOWN CATEGORIES
               ================================================= */

            categoryOrder.forEach(
                category => {

                    const value =
                        Number(
                            categories[category]
                            || 0
                        );


                    knownTotal += value;


                    if (value <= 0) {

                        return;

                    }


                    const segment =
                        createThreatSegment(
                            category,
                            value,
                            maxValue
                        );


                    stack.appendChild(
                        segment
                    );

                }
            );


            /* =================================================
               OTHER CATEGORIES
               ================================================= */

            const total =
                Object.values(
                    categories
                ).reduce(
                    (
                        sum,
                        value
                    ) =>
                        sum +
                        Number(value || 0),
                    0
                );


            const other =
                total -
                knownTotal;


            if (other > 0) {

                const segment =
                    createThreatSegment(
                        "Other",
                        other,
                        maxValue
                    );


                stack.appendChild(
                    segment
                );

            }


            /* =================================================
               TIME LABEL
               ================================================= */

            const timeLabel =
                document.createElement(
                    "span"
                );


            timeLabel.className =
                "threat-time-label";


            timeLabel.textContent =
                formatChartTime(
                    item.timestamp
                );


            column.appendChild(
                stack
            );


            column.appendChild(
                timeLabel
            );


            container.appendChild(
                column
            );

        }
    );

}


/* =========================================================
   CREATE THREAT SEGMENT
   ========================================================= */

function createThreatSegment(
    category,
    value,
    maxValue
) {

    const segment =
        document.createElement(
            "div"
        );


    segment.className =
        "threat-segment";


    segment.classList.add(
        getThreatCategoryClass(category)
    );


    const height =
        Math.max(
            3,
            (Number(value) / maxValue) * 230
        );


    segment.style.height =
        `${height}px`;


    segment.title =
        `${category}: ${value}`;


    return segment;

}


/* =========================================================
   THREAT CATEGORY CSS CLASS
   ========================================================= */

function getThreatCategoryClass(category) {

    switch (category) {

        case "Generic":

            return "threat-generic";


        case "Exploits":

            return "threat-exploits";


        case "DoS":

            return "threat-dos";


        case "Fuzzers":

            return "threat-fuzzers";


        default:

            return "threat-other";

    }

}


/* =========================================================
   SET TEXT HELPER
   ========================================================= */

function setText(elementId, value) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {

        console.warn(
            `Element #${elementId} was not found.`
        );

        return;

    }


    element.textContent =
        value ?? 0;

}


/* =========================================================
   ALERT TABLE
   ========================================================= */

function renderAlerts(alerts) {

    const tbody =
        document.getElementById(
            "alertsTable"
        );


    if (!tbody) {

        console.warn(
            "#alertsTable was not found."
        );

        return;

    }


    tbody.innerHTML = "";


    if (
        !alerts ||
        alerts.length === 0
    ) {

        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    No alerts found.
                </td>
            </tr>
        `;

        return;

    }


    alerts.forEach(
        alert => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${formatDate(
                        alert.timestamp
                    )}
                </td>


                <td>
                    ${escapeHtml(
                        alert.type
                    )}
                </td>


                <td>

                    <span
                        class="severity ${getSeverityClass(
                            alert.severity
                        )}">

                        ${escapeHtml(
                            alert.severity
                        )}

                    </span>

                </td>


                <td>
                    ${escapeHtml(
                        alert.description
                    )}
                </td>


                <td>

                    <span class="status">

                        ${escapeHtml(
                            alert.status
                        )}

                    </span>

                </td>

            `;


            tbody.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   TRAFFIC TABLE
   ========================================================= */

function renderTraffic(traffic) {

    const tbody =
        document.getElementById(
            "trafficTable"
        );


    if (!tbody) {

        console.warn(
            "#trafficTable was not found."
        );

        return;

    }


    tbody.innerHTML = "";


    if (
        !traffic ||
        traffic.length === 0
    ) {

        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No traffic records found.
                </td>
            </tr>
        `;

        return;

    }


    traffic.forEach(
        log => {

            const row =
                document.createElement(
                    "tr"
                );


            const predictionClass =
                log.prediction === "Attack"
                    ? "attack"
                    : "normal";


            row.innerHTML = `

                <td>
                    #${log.id}
                </td>


                <td>
                    ${formatDate(
                        log.timestamp
                    )}
                </td>


                <td>

                    <span
                        class="${predictionClass}">

                        ${escapeHtml(
                            log.prediction
                        )}

                    </span>

                </td>


                <td>
                    ${escapeHtml(
                        log.attack_category || "-"
                    )}
                </td>


                <td>
                    ${escapeHtml(
                        log.protocol || "-"
                    )}
                </td>


                <td>
                    ${escapeHtml(
                        log.service || "-"
                    )}
                </td>


                <td>
                    ${
                        (
                            Number(
                                log.confidence
                            ) * 100
                        ).toFixed(1)
                    }%
                </td>

            `;


            tbody.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   SEVERITY CLASS
   ========================================================= */

function getSeverityClass(severity) {

    if (!severity) {

        return "";

    }


    return severity
        .toLowerCase()
        .replace(/\s+/g, "-");

}


/* =========================================================
   DATE FORMAT
   ========================================================= */

function formatDate(timestamp) {

    if (!timestamp) {

        return "-";

    }


    const date =
        new Date(timestamp);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return timestamp;

    }


    return date.toLocaleString();

}


/* =========================================================
   HTML ESCAPE
   ========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   LIVE DASHBOARD REFRESH
   ========================================================= */

async function refreshDashboard() {

    console.log(
        "Refreshing ThreatX dashboard..."
    );


    try {

        await Promise.all([
            loadStatistics(),
            loadAlerts(),
            loadTraffic(),
            loadAnalytics()
        ]);


        console.log(
            "ThreatX dashboard refreshed successfully."
        );


    } catch (error) {

        console.error(
            "Dashboard refresh failed:",
            error
        );

    }

}


/* =========================================================
   START LIVE REFRESH
   ========================================================= */

function startLiveRefresh() {

    if (liveRefreshTimer !== null) {

        return;

    }


    console.log(
        "ThreatX live dashboard refresh started."
    );


    liveRefreshTimer =
        setInterval(
            refreshDashboard,
            LIVE_REFRESH_INTERVAL
        );

}


/* =========================================================
   STOP LIVE REFRESH
   ========================================================= */

function stopLiveRefresh() {

    if (
        liveRefreshTimer !== null
    ) {

        clearInterval(
            liveRefreshTimer
        );


        liveRefreshTimer = null;


        console.log(
            "ThreatX live dashboard refresh stopped."
        );

    }

}


/* =========================================================
   LIVE MONITORING CONTROLS
   ========================================================= */

function getMonitoringElements() {

    return {

        startButton:
            document.getElementById(
                "startSimulationButton"
            ),

        stopButton:
            document.getElementById(
                "stopSimulationButton"
            ),

        statusDot:
            document.getElementById(
                "liveStatusDot"
            ),

        statusText:
            document.getElementById(
                "liveStatusText"
            ),

        statusDescription:
            document.getElementById(
                "liveStatusDescription"
            )

    };

}


/* =========================================================
   SET MONITORING STATUS
   ========================================================= */

function setMonitoringStatus(isRunning) {

    const elements =
        getMonitoringElements();


    if (
        !elements.statusDot ||
        !elements.statusText ||
        !elements.statusDescription ||
        !elements.startButton ||
        !elements.stopButton
    ) {

        console.warn(
            "Live monitoring elements were not found."
        );

        return;

    }


    if (isRunning) {

        elements.statusDot.classList.remove(
            "offline"
        );


        elements.statusDot.classList.add(
            "online"
        );


        elements.statusText.textContent =
            "Monitoring Live";


        elements.statusDescription.textContent =
            "ThreatX is monitoring incoming network traffic.";


        elements.startButton.disabled =
            true;


        elements.stopButton.disabled =
            false;


    } else {

        elements.statusDot.classList.remove(
            "online"
        );


        elements.statusDot.classList.add(
            "offline"
        );


        elements.statusText.textContent =
            "Monitoring Stopped";


        elements.statusDescription.textContent =
            "Start the traffic stream to monitor network activity in real time.";


        elements.startButton.disabled =
            false;


        elements.stopButton.disabled =
            true;

    }

}


/* =========================================================
   LOAD REAL BACKEND MONITORING STATUS
   ========================================================= */

async function loadSimulationStatus() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/simulation/status`
            );


        if (!response.ok) {

            throw new Error(
                `Simulation status API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Simulation status:",
            data
        );


        setMonitoringStatus(
            Boolean(data.running)
        );


    } catch (error) {

        console.error(
            "Failed to load simulation status:",
            error
        );


        /*
         * Do not pretend that monitoring is running
         * if the backend cannot be reached.
         */

        setMonitoringStatus(false);

    }

}


/* =========================================================
   START BACKEND MONITORING
   ========================================================= */

async function startMonitoring() {

    const elements =
        getMonitoringElements();


    if (!elements.startButton) {

        return;

    }


    try {

        elements.startButton.disabled =
            true;


        if (elements.statusText) {

            elements.statusText.textContent =
                "Starting Monitoring...";

        }


        if (elements.statusDescription) {

            elements.statusDescription.textContent =
                "Starting the network traffic simulation.";

        }


        console.log(
            "Starting ThreatX monitoring..."
        );


        const response =
            await fetch(
                `${API_BASE_URL}/api/simulation/start`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Start API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Simulation start response:",
            data
        );


        setMonitoringStatus(
            Boolean(data.running)
        );


        /*
         * Immediately refresh dashboard
         * instead of waiting 3 seconds.
         */

        refreshDashboard();


    } catch (error) {

        console.error(
            "Failed to start monitoring:",
            error
        );


        setMonitoringStatus(false);


        if (elements.statusDescription) {

            elements.statusDescription.textContent =
                "Unable to start monitoring. Check that the ThreatX backend is running.";

        }

    }

}


/* =========================================================
   STOP BACKEND MONITORING
   ========================================================= */

async function stopMonitoring() {

    const elements =
        getMonitoringElements();


    if (!elements.stopButton) {

        return;

    }


    try {

        elements.stopButton.disabled =
            true;


        if (elements.statusText) {

            elements.statusText.textContent =
                "Stopping Monitoring...";

        }


        if (elements.statusDescription) {

            elements.statusDescription.textContent =
                "Stopping the network traffic simulation.";

        }


        console.log(
            "Stopping ThreatX monitoring..."
        );


        const response =
            await fetch(
                `${API_BASE_URL}/api/simulation/stop`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Stop API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Simulation stop response:",
            data
        );


        setMonitoringStatus(
            Boolean(data.running)
        );


    } catch (error) {

        console.error(
            "Failed to stop monitoring:",
            error
        );


        /*
         * Ask backend for the real state
         * instead of guessing.
         */

        await loadSimulationStatus();

    }

}


/* =========================================================
   SYNCHRONIZE MONITORING STATUS
   ========================================================= */

setInterval(
    loadSimulationStatus,
    LIVE_REFRESH_INTERVAL
);