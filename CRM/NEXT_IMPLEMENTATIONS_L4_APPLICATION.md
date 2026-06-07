# NEXT IMPLEMENTATIONS - SUITE LOGIQUE L4 APPLICATION (CRM + FNE)

Date: 2026-03-05  
Contexte: INT-01 a INT-10 livrees. Le socle ventes/facturation/FNE est operationnel et neutralise multi-tenant.

## 1) Point de depart

- Etat actuel:
  - Flux bout-en-bout disponible: vente -> facture -> certification FNE -> paiement -> sync finance.
  - Qualite/observabilite finance active (INT-09).
  - Noyau reusable multi-tenant actif (INT-10).
- Gap principal:
  - G5 (UAT metier) et G6 (preprod/prod readiness) restent a finaliser.
- Objectif L4:
  - passer de "MVP premium technique valide" a "application exploitable, replicable, commercialisable a grande echelle".

## 2) Backlog priorise des prochaines implementations

## P0 - Critique (go-live et replication client)

### INT-11 - UAT metier formalisee Ventes/FNE
- Resultat attendu:
  - UAT signee par metier (vente, caisse, compta, conformite) sur scenarios reels.
- Scope:
  - pack de scenarios UAT (happy path + rejet FNE + avoir + paiement partiel + correction donnees fiscales).
  - jeu de donnees de reference (clients, produits, factures, paiements).
  - PV de validation avec ecarts et decision GO/NO-GO.
- Dependances:
  - INT-01 a INT-10.
- References code:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/sales.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/integrations.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/governance.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/observability.py`
- References tests:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/tests/test_sales_phase6_credit_notes.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/tests/test_sales_phase7_payments.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/tests/test_enterprise_connectors_phase5.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/tests/test_governance_phase9_finance.py`
- Sorties livrables:
  - `markdown/uat_vfne_plan.md`
  - `markdown/uat_vfne_results_YYYYMMDD.md`

### INT-12 - Preprod/Prod readiness pack (G6)
- Resultat attendu:
  - runbook d exploitation complet + exercices incident/rollback passes.
- Scope:
  - checklist preprod/prod (monitoring, logs, backups, restore, rollback).
  - parametrage seuils observabilite production.
  - crons systemes valides (SLA, observabilite, connecteurs).
  - procedure de gestion incident (P1/P2/P3) avec RTO/RPO.
- Dependances:
  - INT-11.
- References code/ops:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/run_sla_orchestration.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/run_observability_checks.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/run_enterprise_connectors.py`
  - `/home/kayz/Documents/maridav.ci-2/markdown/observability_incident_runbook.md`
  - `/home/kayz/Documents/maridav.ci-2/markdown/enterprise_connectors_runbook.md`
- Sorties livrables:
  - `markdown/preprod_prod_readiness_checklist.md`
  - `markdown/drill_incident_rollback_report.md`

### INT-13 - Bootstrap tenant automatise (onboarding client en 1 commande)
- Resultat attendu:
  - creation d un tenant complet (branding, roles, connecteurs seeds, profile env) sans intervention manuelle lourde.
- Scope:
  - nouvelle commande `bootstrap_tenant`:
    - initialise variables/parametres tenant.
    - execute `setup_roles` + `setup_enterprise_connectors`.
    - genere un kit client + manifest d activation.
  - output standardise pour equipe delivery.
- Dependances:
  - INT-10.
- References code:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/tenant.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/context_processors.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/build_packplus_client_kit.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/setup_roles.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/management/commands/setup_enterprise_connectors.py`
- Sorties livrables:
  - commande `python manage.py bootstrap_tenant ...`
  - `markdown/tenant_onboarding_runbook.md`

## P1 - Haute valeur (fiabilite et monetisation)

### INT-14 - Archive legale facture FNE (evidence complete)
- Resultat attendu:
  - chaque facture dispose d un dossier preuve complet (pdf, payload, statut, references, timeline).
- Scope:
  - stockage immuable des payloads FNE envoyes/retours.
  - index de recherche par facture/periode/client.
  - export dossier audit (zip preuve par facture).
- Dependances:
  - INT-03/04/09.
- References code:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/models.py` (Invoice, AuditTrail)
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/integrations.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/templates/crm/sales/print.html`
- Sorties livrables:
  - app/service `fne_archive` (ou extension crm)
  - endpoint export dossier preuve

### INT-15 - Cockpit executive finance/compliance
- Resultat attendu:
  - dashboard direction avec KPI actionnables (cash, impayes, rejets FNE, DSO, latence certification).
- Scope:
  - KPI agreges par jour/semaine/mois.
  - drill-down par commercial, client, region, canal paiement.
  - alertes metiers (pas seulement techniques).
- Dependances:
  - INT-07/08/09.
- References code:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/observability.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/views.py` (DashboardView)
  - `/home/kayz/Documents/maridav.ci-2/CRM/templates/crm/dashboard.html`
- Sorties livrables:
  - `crm/services/finance_kpi.py`
  - vue dashboard finance/compliance

### INT-16 - Durcissement securite donnees et retention
- Resultat attendu:
  - politique de retention/anonymisation active pour donnees sensibles (PII, pieces RH, logs).
- Scope:
  - classification donnees sensibles.
  - regles retention par type d objet.
  - jobs de purge/anonymisation traces et auditables.
- Dependances:
  - INT-12.
- References code/docs:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/security_middleware.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/governance.py`
  - `/home/kayz/Documents/maridav.ci-2/current_context.md` (invariants)
- Sorties livrables:
  - commande `run_data_retention_policies`
  - `markdown/data_retention_policy.md`

## P2 - Scale (performance et produit multi-entreprises)

### INT-17 - Migration runtime production vers PostgreSQL + tuning
- Resultat attendu:
  - stack DB production-grade, plans indexes et perf valides sur charge reelle.
- Scope:
  - bascule settings DB de sqlite vers postgres.
  - indexes metier sur facturation/paiements/connecteurs.
  - tests de charge API et batch connectors.
- Dependances:
  - INT-12.
- References:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm_project/settings.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/models.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/integrations.py`
- Sorties livrables:
  - guide migration DB
  - rapport perf `markdown/perf_baseline_postgres.md`

### INT-18 - Portail configuration tenant self-service (admin plateforme)
- Resultat attendu:
  - equipe delivery/ops configure un nouveau tenant depuis UI admin interne.
- Scope:
  - CRUD tenant profile (branding, domaines, cookies, connecteurs).
  - validation coherence parametres avant activation.
  - historique des changements de configuration.
- Dependances:
  - INT-13.
- References:
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/services/tenant.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/admin.py`
  - `/home/kayz/Documents/maridav.ci-2/CRM/crm/api/views.py`
- Sorties livrables:
  - modele `TenantConfig` (si retention dans DB)
  - UI admin + API securisee

## 3) Sequence recommandee (execution)

1. INT-11 (UAT metier)  
2. INT-12 (preprod/prod readiness)  
3. INT-13 (bootstrap tenant automatise)  
4. INT-14 (archive legale FNE)  
5. INT-15 (cockpit executive)  
6. INT-16 (retention/securite donnees)  
7. INT-17 (postgres + perf)  
8. INT-18 (portail tenant self-service)

## 4) References transverses obligatoires

- Pilotage:
  - `/home/kayz/Documents/maridav.ci-2/CRM/work.md`
  - `/home/kayz/Documents/maridav.ci-2/CRM/IMPLEMENTATIONS_RECAP.md`
- Contexte architecture:
  - `/home/kayz/Documents/maridav.ci-2/current_context.md`
  - `/home/kayz/Documents/maridav.ci-2/phases_industrialisation.md`
- Productisation:
  - `/home/kayz/Documents/maridav.ci-2/Waas_PackPlus.md`
  - `/home/kayz/Documents/maridav.ci-2/markdown/waasplus_productisation_runbook.md`
- Exploitation:
  - `/home/kayz/Documents/maridav.ci-2/markdown/observability_incident_runbook.md`
  - `/home/kayz/Documents/maridav.ci-2/markdown/enterprise_connectors_runbook.md`

## 5) Commandes de controle standard (a executer sur chaque increment)

```bash
cd /home/kayz/Documents/maridav.ci-2/CRM
source .maridav/bin/activate
python manage.py check
python manage.py test -v 1
python manage.py run_sla_orchestration
python manage.py run_observability_checks --window-minutes 5
python manage.py run_enterprise_connectors
```

## 6) Critere de passage a l implementation suivante

- Gate G2: code/migrations/permissions completes + `check` vert.
- Gate G3: tests cibles + regression package vertes.
- Gate G4: QA fonctionnelle sans bug bloquant.
- Gate G5: validation metier signee.
- Gate G6: readiness preprod/prod validee.

Regle: NO-GO sur un gate = retour a l integration precedente.
