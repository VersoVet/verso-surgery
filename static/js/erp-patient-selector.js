/**
 * ErpPatientSelector - Standalone component for selecting patients
 *
 * Usage:
 *   const selector = new ErpPatientSelector({
 *     container: document.getElementById('patient-selector'),
 *     apiBase: '/api/dashboard',
 *     onSelect: (patient) => console.log(patient),
 *     defaultSiteId: 2
 *   });
 *   await selector.init();
 */

class ErpPatientSelector {
  constructor(options = {}) {
    this.container = options.container || document.body;
    this.apiBase = options.apiBase || '/api/dashboard';
    this.onSelect = options.onSelect || (() => {});
    this.defaultSiteId = options.defaultSiteId || 2;

    // State
    this.sites = [];
    this.vets = [];
    this.appointments = [];
    this.selectedSiteId = this.defaultSiteId;
    this.selectedVetId = null;
    this.selectedDate = this._getTodayString();

    // Cache
    this.cache = {
      sites: null,
      vets: null,
    };

    this._render();
  }

  /**
   * Initialize the component (fetch data and attach listeners).
   */
  async init() {
    try {
      this._loadCookies();
      await this._loadSites();
      await this._loadVets();
      await this._loadAppointments();
      this._attachListeners();
    } catch (error) {
      console.error('ErpPatientSelector init failed:', error);
    }
  }

  /**
   * Refresh appointments for the current date.
   */
  async refresh() {
    await this._loadAppointments();
    this._renderAppointments();
  }

  /**
   * Reset the selector to initial state.
   */
  reset() {
    this.selectedSiteId = this.defaultSiteId;
    this.selectedVetId = null;
    this.selectedDate = this._getTodayString();
    this.appointments = [];
    this._render();
  }

  // ===== PRIVATE METHODS =====

  /**
   * Get today's date as YYYY-MM-DD string.
   */
  _getTodayString() {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }

  /**
   * Save site and vet selections to cookies (90 days).
   */
  _saveCookies() {
    const expires = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = `erp_site_id=${this.selectedSiteId}; expires=${expires}; path=/`;
    if (this.selectedVetId) {
      document.cookie = `erp_vet_id=${this.selectedVetId}; expires=${expires}; path=/`;
    } else {
      document.cookie = `erp_vet_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
    }
  }

  /**
   * Load site and vet selections from cookies.
   */
  _loadCookies() {
    const cookies = Object.fromEntries(
      document.cookie.split(';').map(c => {
        const [k, v] = c.trim().split('=');
        return [decodeURIComponent(k), decodeURIComponent(v || '')];
      })
    );
    if (cookies.erp_site_id) {
      this.selectedSiteId = parseInt(cookies.erp_site_id) || this.defaultSiteId;
    }
    if (cookies.erp_vet_id && cookies.erp_vet_id !== '') {
      this.selectedVetId = cookies.erp_vet_id;
    }
  }

  /**
   * Render the initial UI structure.
   */
  _render() {
    this.container.innerHTML = `
      <div class="erp-patient-selector">
        <style>
          .erp-patient-selector {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 600px;
          }
          .erp-selector-row {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
          }
          .erp-selector-col {
            flex: 1;
            min-width: 200px;
          }
          .erp-selector-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #4F46E5;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
          .erp-selector-input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            background: white;
          }
          .erp-selector-input:focus {
            outline: none;
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
          }
          .erp-appointments-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            background: white;
          }
          .erp-apt-row {
            padding: 12px 16px;
            border-bottom: 1px solid #E5E7EB;
            cursor: pointer;
            transition: background-color 0.2s;
          }
          .erp-apt-row:hover {
            background-color: #F9FAFB;
          }
          .erp-apt-row:last-child {
            border-bottom: none;
          }
          .erp-apt-time {
            font-size: 13px;
            font-weight: 600;
            color: #4F46E5;
            margin-bottom: 4px;
          }
          .erp-apt-animal {
            font-size: 14px;
            font-weight: 500;
            color: #1F2937;
            margin-bottom: 2px;
          }
          .erp-apt-client {
            font-size: 12px;
            color: #6B7280;
            margin-bottom: 2px;
          }
          .erp-apt-reason {
            font-size: 12px;
            color: #9CA3AF;
            font-style: italic;
          }
          .erp-no-results {
            padding: 24px;
            text-align: center;
            color: #9CA3AF;
            font-size: 14px;
          }
          .erp-loading {
            padding: 16px;
            text-align: center;
            color: #6B7280;
            font-size: 13px;
          }
        </style>

        <div class="erp-selector-row">
          <div class="erp-selector-col">
            <label class="erp-selector-label">Site</label>
            <select id="erp-site-select" class="erp-selector-input">
              <option value="">Chargement...</option>
            </select>
          </div>
          <div class="erp-selector-col">
            <label class="erp-selector-label">Vétérinaire</label>
            <select id="erp-vet-select" class="erp-selector-input">
              <option value="">Tous les vétérinaires</option>
            </select>
          </div>
        </div>

        <div class="erp-selector-row">
          <div class="erp-selector-col">
            <label class="erp-selector-label">Date</label>
            <input
              type="date"
              id="erp-date-input"
              class="erp-selector-input"
              value="${this.selectedDate}"
            />
          </div>
        </div>

        <div id="erp-appointments-container">
          <div class="erp-no-results">Sélectionnez une date</div>
        </div>
      </div>
    `;
  }

  /**
   * Attach event listeners to UI elements.
   */
  _attachListeners() {
    const siteSelect = this.container.querySelector('#erp-site-select');
    const vetSelect = this.container.querySelector('#erp-vet-select');
    const dateInput = this.container.querySelector('#erp-date-input');

    if (siteSelect) {
      siteSelect.addEventListener('change', async (e) => {
        this.selectedSiteId = parseInt(e.target.value) || this.defaultSiteId;
        this._saveCookies();
        await this._loadAppointments();
        this._renderAppointments();
      });
    }

    if (vetSelect) {
      vetSelect.addEventListener('change', (e) => {
        this.selectedVetId = e.target.value || null;
        this._saveCookies();
        this._filterAndRenderAppointments();
      });
    }

    if (dateInput) {
      dateInput.addEventListener('change', async (e) => {
        this.selectedDate = e.target.value;
        await this._loadAppointments();
        this._renderAppointments();
      });
    }
  }

  /**
   * Load sites from API.
   */
  async _loadSites() {
    if (this.cache.sites) {
      this.sites = this.cache.sites;
      this._renderSites();
      return;
    }

    try {
      const response = await fetch(`${this.apiBase}/sites`);
      const data = await response.json();
      this.sites = data.sites || [];
      this.cache.sites = this.sites;
      this._renderSites();
    } catch (error) {
      console.error('Failed to load sites:', error);
      this.sites = [];
    }
  }

  /**
   * Load vets from API.
   */
  async _loadVets() {
    if (this.cache.vets) {
      this.vets = this.cache.vets;
      this._renderVets();
      return;
    }

    try {
      const response = await fetch(`${this.apiBase}/vets`);
      const data = await response.json();
      this.vets = data.vets || [];
      this.cache.vets = this.vets;
      this._renderVets();
    } catch (error) {
      console.error('Failed to load vets:', error);
      this.vets = [];
    }
  }

  /**
   * Load appointments for selected date range.
   */
  async _loadAppointments() {
    try {
      const params = new URLSearchParams({
        date_from: this.selectedDate,
        date_to: this.selectedDate,
        site_id: this.selectedSiteId,
      });

      const response = await fetch(`${this.apiBase}/appointments?${params}`);
      const data = await response.json();
      this.appointments = data.appointments || [];
    } catch (error) {
      console.error('Failed to load appointments:', error);
      this.appointments = [];
    }
  }

  /**
   * Render sites in the select dropdown.
   */
  _renderSites() {
    const siteSelect = this.container.querySelector('#erp-site-select');
    if (!siteSelect) return;

    siteSelect.innerHTML = this.sites
      .map((site) => `<option value="${site.id}">${site.nom}</option>`)
      .join('');

    // Select site (use selectedSiteId which may be from cookie)
    if (this.selectedSiteId) {
      siteSelect.value = this.selectedSiteId;
    }
  }

  /**
   * Render vets in the select dropdown.
   */
  _renderVets() {
    const vetSelect = this.container.querySelector('#erp-vet-select');
    if (!vetSelect) return;

    vetSelect.innerHTML =
      '<option value="">Tous les vétérinaires</option>' +
      this.vets
        .map((vet) => `<option value="${vet.id}">${vet.nom}</option>`)
        .join('');

    // Pre-select vet from cookie if available
    if (this.selectedVetId) {
      vetSelect.value = this.selectedVetId;
    }
  }

  /**
   * Filter appointments by vet and render them.
   */
  _filterAndRenderAppointments() {
    let filtered = this.appointments;

    // Filter by vet if selected (use string comparison to handle type coercion)
    if (this.selectedVetId) {
      filtered = filtered.filter((apt) => String(apt.vet_id) === String(this.selectedVetId));
    }

    // Render
    const container = this.container.querySelector('#erp-appointments-container');
    if (!container) return;

    if (filtered.length === 0) {
      container.innerHTML = '<div class="erp-no-results">Aucun RDV trouvé</div>';
      return;
    }

    container.innerHTML =
      '<div class="erp-appointments-list">' +
      filtered.map((apt) => this._renderAppointmentRow(apt)).join('') +
      '</div>';
  }

  /**
   * Render a single appointment row.
   */
  _renderAppointmentRow(apt) {
    const time = apt.datetime_consult
      ? apt.datetime_consult.substring(11, 16)
      : '--:--';

    return `
      <div class="erp-apt-row" onclick="window._erpPatientSelectorInstance && window._erpPatientSelectorInstance._selectAppointment(${JSON.stringify(apt).replace(/"/g, '&quot;')})">
        <div class="erp-apt-time">${time}</div>
        <div class="erp-apt-animal">${apt.animal_nom} (${apt.espece})</div>
        <div class="erp-apt-client">${apt.client_prenom} ${apt.client_nom}</div>
        <div class="erp-apt-reason">${apt.motif || '—'}</div>
      </div>
    `;
  }

  /**
   * Render all appointments.
   */
  _renderAppointments() {
    this._filterAndRenderAppointments();
  }

  /**
   * Handle appointment selection.
   */
  _selectAppointment(apt) {
    const patient = {
      animal_id: apt.animal_id,
      animal_nom: apt.animal_nom,
      espece: apt.espece,
      race: apt.race || '',
      poids: apt.poids || 0,
      client_id: apt.client_id,
      client_nom: apt.client_nom,
      client_prenom: apt.client_prenom,
      date_rdv: apt.date_rdv || this.selectedDate,
    };

    if (this.onSelect) {
      this.onSelect(patient);
    }
  }
}

// Make component available globally
window.ErpPatientSelector = ErpPatientSelector;
