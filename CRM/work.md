# WORKPLAN MVP PREMIUM - MARIDAV CI (FNE COMMAND LAYER)

Date: 2026-03-05  
Owner: Produit + Tech + Conformite

## 1) Objectif

Construire un MVP **PREMIUM** de ventes/facturation conforme FNE, sans cassure, avec un workflow robuste de bout en bout:

- capture vente
- emission facture
- certification FNE
- suivi statuts
- blocage automatique des operations non conformes
- pilotage qualite et observabilite

Regle d'or: **pas de passage a l'integration suivante tant que la precedente n'est pas validee a 100%.**

---

## 2) Integrations cibles (10) - ordre d'execution obligatoire

### INT-01 - Ventes Express + Facturation CRM
- Portee: creation/edition/impression facture, lignes, calculs, commercial responsable.
- Resultat attendu: flux de vente operationnel en UI + API.
- Dependances: aucune.

### INT-02 - Profil fiscal client obligatoire
- Portee: NCC, NTD, RCCM, regime fiscal + controles de completude.
- Resultat attendu: donnees fiscales presentes avant emission finale.
- Dependances: INT-01.

### INT-03 - Connecteur FNE outbound (certification facture)
- Portee: emission evenement facture vers FNE (outbox), mapping champs, idempotence.
- Resultat attendu: facture envoyee au moteur FNE avec tracking.
- Dependances: INT-01, INT-02.

### INT-04 - Connecteur FNE inbound (retours statuts)
- Portee: reception statuts FNE (pending/certified/rejected), reference, erreurs.
- Resultat attendu: statut FNE synchronise automatiquement dans le CRM.
- Dependances: INT-03.

### INT-05 - Gate de conformite operationnelle (blocage strict)
- Portee: bloquer livraison/compta/finalisation si facture non certifiee FNE (hors exception tracee).
- Resultat attendu: zero operation aval non conforme.
- Dependances: INT-03, INT-04.

### INT-06 - Workflow d'avoir / annulation conforme
- Portee: emission avoir, lien facture source, synchro FNE des corrections.
- Resultat attendu: correction post-facturation traçable et conforme.
- Dependances: INT-05.

### INT-07 - Reconciliation paiements (caisse/MM/virement)
- Portee: rapprochement paiement <-> facture, statuts payee/partiellement payee.
- Resultat attendu: coherence comptable en temps reel.
- Dependances: INT-01.

### INT-08 - Connecteur ERP/Compta
- Portee: push des factures et statuts vers ERP/compta.
- Resultat attendu: continuité finance sans resaisie manuelle.
- Dependances: INT-01, INT-07.

### INT-09 - Gouvernance qualite + audit + observabilite
- Portee: data quality issues, audit trail, alerting SLA, dashboards conformite.
- Resultat attendu: supervision continue et audit-ready.
- Dependances: INT-01 a INT-08.

### INT-10 - Industrialisation MVP neutre (core reusable)
- Portee: extraire noyau neutralise (apps/services), conserver couche Maridav comme premier tenant.
- Resultat attendu: base produit repliquable pour autres entreprises.
- Dependances: INT-01 a INT-09.

---

## 3) Systeme de controle des implementations (Control Tower)

## Etats autorises

1. `PLANNED`
2. `READY`
3. `IN_PROGRESS`
4. `DEV_DONE`
5. `QA_PASS`
6. `UAT_PASS`
7. `PROD_READY`
8. `DONE`

Transition bloquante: une integration ne passe a l'etat suivant que si toutes les evidences sont validees.

---

## 4) Quality Gates obligatoires (GO / NO-GO)

### Gate G0 - Scope lock (avant dev)
- User stories et acceptance criteria figes.
- Impacts techniques listes (models, views, API, jobs, permissions, migrations).
- Plan de rollback defini.

### Gate G1 - Design lock
- Architecture validee.
- Risques identifies + plan mitigation.
- Cas limites (erreurs API, timeout, doublons, indisponibilite FNE) documentes.

### Gate G2 - Dev completion
- Code complet + migrations + seeds + permissions.
- Aucun TODO critique.
- `python manage.py check` OK.

### Gate G3 - Tests techniques
- Tests unitaires + integration passes.
- Couverture des cas critiques (happy path + failure path + retry + idempotence).
- Regression package cible vert.

### Gate G4 - QA fonctionnelle
- Scenarios fonctionnels executes et valides.
- Aucun bug bloquant/majeur ouvert.

### Gate G5 - UAT metier
- Validation metier (vente, compta, conformite) signee.
- Conformite FNE validee sur echantillon de factures.

### Gate G6 - Preprod/production readiness
- Monitoring/alerting actifs.
- Logs auditables.
- Procedure incident + rollback testee.

### Gate G7 - Post go-live validation
- Verification J+1/J+7.
- Aucun ecart critique.
- Integration marquee `DONE`.

Regle absolue: **NO-GO => retour a l'etat precedent.**

---

## 5) Controle de qualite PREMIUM (score 10/10)

Chaque integration est notee sur 10 axes (1 point chacun):

1. Conformite metier
2. Conformite FNE
3. Robustesse technique
4. Couverture de tests
5. Qualite UX
6. Performance
7. Securite
8. Observabilite
9. Documentation
10. Exploitabilite (runbook/support)

Seuil de passage: `>= 9/10` et **aucun axe critique < 1**.

---

## 6) Checklist d'implémentation standard (a dupliquer par integration)

### Template Integration
- ID:
- Nom:
- Owner:
- Etat:
- Date debut:
- Date fin cible:

### Definition of Ready (DoR)
- [ ] Scope valide
- [ ] AC valides
- [ ] Dependencies disponibles
- [ ] Donnees de test disponibles

### Definition of Done (DoD)
- [ ] Code merge
- [ ] Migration appliquee
- [ ] Permissions/roles mis a jour
- [ ] Tests unitaires/integration verts
- [ ] QA metier validee
- [ ] Monitoring actif
- [ ] Documentation runbook complete

### Evidence Pack (obligatoire)
- [ ] Commandes executees + resultats
- [ ] Captures flux UI/API
- [ ] Matrice tests
- [ ] Rapport ecarts & corrections

---

## 7) Sequencement actif

### Wave A (Fondation)
- INT-01
- INT-02
- INT-03
- INT-04

### Wave B (Conformite dure + Finance)
- INT-05
- INT-06
- INT-07
- INT-08

### Wave C (Excellence operationnelle + Produit)
- INT-09
- INT-10

---

## 8) Journal de pilotage (a tenir a jour)

### 2026-03-05 - Baseline
- Module ventes/factures en place (UI/API/models/services/signals/connecteurs seed de base).
- Prochaine implementation prioritaire: **INT-05 Gate de conformite operationnelle**.
- Action immediate: introduire blocage strict des operations aval tant que `invoice.fne_status != certified` (sauf exception tracee).

### 2026-03-05 - INT-05 implémentée (Gate FNE livraison)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - blocage livraison commande en UI si factures liees non certifiees FNE.
  - blocage livraison commande en API (`PATCH /api/v1/orders/{id}`) tant que non certifie.
  - blocage synchro inbound ERP/logistique si tentative de passage en `delivered` non conforme FNE.
- Evidence code:
  - service gate: `crm/services/sales.py` (`validate_order_fne_delivery_gate`)
  - enforcement UI: `crm/views.py` (`OrderCreateView`, `OrderUpdateView`)
  - enforcement API: `crm/api/views.py` (`OrderViewSet.perform_create/perform_update`)
  - enforcement integration inbox: `crm/services/integrations.py` (`_handle_order_sync_inbox_event`)
- Evidence tests:
  - `test_order_delivery_is_blocked_until_fne_certification`
  - `test_process_inbox_order_delivery_blocked_when_invoice_not_fne_certified`
  - suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_api_security_phase1 crm.tests.test_enterprise_connectors_phase5 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier)
  - G6: A faire (preprod/prod readiness)

### 2026-03-05 - INT-06 implémentée (Workflow avoir / annulation)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - prise en charge des avoirs (`nature=credit_note`) avec lien obligatoire facture d'origine.
  - regles metier sur emission d'avoir (facture source emise et certifiee FNE).
  - prefill UI "creer avoir" depuis facture standard + impression enrichie.
  - auto-annulation facture source en cas d'avoir integral.
- Evidence code:
  - model/metier: `crm/models.py`, `crm/services/sales.py`, `crm/services/governance.py`
  - enforcement et sync: `crm/signals.py`, `crm/services/integrations.py`
  - UI/API/admin: `crm/views.py`, `templates/crm/sales/*`, `crm/api/views.py`, `crm/admin.py`
- Evidence tests:
  - `crm.tests.test_sales_phase6_credit_notes`
  - regression connecteurs phase 5 + suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_sales_phase6_credit_notes crm.tests.test_enterprise_connectors_phase5 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier)
  - G6: A faire (preprod/prod readiness)

### 2026-03-05 - INT-07 implémentée (Réconciliation paiements)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - ledger de paiements `InvoicePayment` (caisse/MM/virement/cheque/credit), source manuelle ou integration.
  - recalcul automatique `paid_amount`, `payment_method`, `payment_reference` sur facture via signaux.
  - transition statut facture auto (`emise` -> `partiellement_payee` -> `payee`) et retour coherent apres suppression paiement.
  - ecrans CRM de saisie paiement + historique paiements sur facture + impression.
  - endpoint API `/api/v1/invoice-payments/` avec controle de scope/permissions.
  - inbound ERP/logistique: traitement `payment.sync` idempotent (dedup par `source_event_id`) vers facture.
- Evidence code:
  - model/migration: `crm/models.py`, `crm/migrations/0015_invoicepayment.py`
  - services metier: `crm/services/sales.py`
  - orchestration signaux: `crm/signals.py`
  - integration inbox/outbox: `crm/services/integrations.py`, `crm/management/commands/setup_enterprise_connectors.py`
  - UI/API/admin: `crm/forms.py`, `crm/views.py`, `crm/urls.py`, `crm/api/views.py`, `crm/api/urls.py`, `crm/api/serializers.py`, `crm/admin.py`, `templates/crm/sales/*`
  - access scope: `crm/services/access_scope.py`
- Evidence tests:
  - `crm.tests.test_sales_phase7_payments`
  - `test_process_inbox_payment_sync_creates_payment_and_reconciles_invoice`
  - `test_process_inbox_payment_sync_is_idempotent_on_source_event`
  - `test_post_invoice_payment_outside_scope_is_blocked`
  - suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_sales_phase7_payments crm.tests.test_enterprise_connectors_phase5 crm.tests.test_api_security_phase1 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier)
  - G6: A faire (preprod/prod readiness)

### 2026-03-05 - INT-08 implémentée (Connecteur ERP/Compta finance)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - flux outbox dedie `invoice_payment.*` pour ERP/Compta et BI (creation/mise a jour/suppression paiement).
  - payload normalise paiement (facture, montant, mode, reference, horodatage, source, provenance connecteur).
  - emission automatique des evenements paiement depuis signaux metier.
  - seed mappings enterprise enrichi pour `invoice_payment` + `inbox:payment.sync`.
- Evidence code:
  - payload + emission: `crm/services/integrations.py` (`build_invoice_payment_payload`, `emit_invoice_payment_outbox_event`)
  - orchestration evenementielle: `crm/signals.py` (`invoice_payment_post_save`, `invoice_payment_post_delete`)
  - mappings connecteurs: `crm/management/commands/setup_enterprise_connectors.py`
- Evidence tests:
  - `test_emit_invoice_payment_outbox_event_targets_erp_and_bi`
  - regression connecteurs phase 5 + suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_enterprise_connectors_phase5 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier)
  - G6: A faire (preprod/prod readiness)

### 2026-03-05 - INT-09 implémentée (Gouvernance qualite + audit + observabilite)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - data quality finance facture renforcée:
    - détection mismatch `paid_amount` vs somme ledger paiements
    - détection paiement sans mode exploitable
    - auto-résolution des anomalies devenues caduques après correction
  - observabilité enrichie avec un bloc `finance`:
    - volume anomalies data quality facture ouvertes/critique
    - incohérences ledger paiements ouvertes
    - factures échues non soldées (nombre + montant)
    - volume factures rejetées FNE
  - alerting observabilité étendu:
    - `finance_dq_open_high`
    - `finance_dq_critical_present`
    - `finance_payment_ledger_mismatch_open`
    - `finance_overdue_amount_high`
    - `finance_fne_rejected_present`
  - récap exécution produit livré dans `IMPLEMENTATIONS_RECAP.md`.
- Evidence code:
  - gouvernance: `crm/services/governance.py`
  - observabilité: `crm/services/observability.py`
  - récap produit: `IMPLEMENTATIONS_RECAP.md`
- Evidence tests:
  - `crm.tests.test_governance_phase9_finance`
  - `crm.tests.test_observability_phase4` (inclut cas alertes finance)
  - suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_governance_phase9_finance crm.tests.test_observability_phase4 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier)
  - G6: A faire (preprod/prod readiness)

### 2026-03-05 - INT-10 implémentée (Industrialisation MVP neutre multi-tenant)
- Etat: `DONE` (dev + tests)
- Portee livree:
  - couche tenant reusable ajoutee (`crm/services/tenant.py`) pour piloter identite CRM par variables d environnement.
  - branding CRM branche au contexte global (`crm.context_processors.crm_tenant_branding`) sans hardcode produit.
  - layout principal (`templates/base.html`) rendu configurable (nom plateforme, tagline, logo, sous-titre).
  - settings multi-tenant enrichis (`CRM_TENANT_*`, `CRM_PLATFORM_*`, `CRM_BRAND_*`) avec compatibilite Maridav par defaut.
  - commande PackPlus enrichie:
    - `tenant_profile.json`
    - variables env tenant/cookies dans `deployment.env.example`
    - bloc `tenant_profile` dans `manifest.json`
- Evidence code:
  - socle tenant: `crm/services/tenant.py`
  - injection contexte: `crm/context_processors.py`, `crm_project/settings.py`
  - UI configurable: `templates/base.html`
  - productisation: `crm/management/commands/build_packplus_client_kit.py`
- Evidence tests:
  - `crm.tests.test_tenant_productisation_phase10`
  - `crm.tests.test_packplus_productisation_phase6` (regression adaptee)
  - suite CRM complete verte.
- Commandes de validation executees:
  - `python manage.py check`
  - `python manage.py test crm.tests.test_packplus_productisation_phase6 crm.tests.test_tenant_productisation_phase10 -v 2`
  - `python manage.py test crm.tests -v 1`
- Gate quality:
  - G2: PASS
  - G3: PASS
  - G4: PASS (niveau technique)
  - G5: A faire (UAT metier multi-tenant)
  - G6: A faire (preprod/prod readiness)

### Prochaine implementation prioritaire
- **Wave post-MVP**: UAT metier complet + readiness preprod/prod + runbook go-live multi-tenant.

### 2026-03-05 - Roadmap L4 documentee
- Livrable ajoute:
  - `NEXT_IMPLEMENTATIONS_L4_APPLICATION.md`
- Portee:
  - priorisation des suites logiques INT-11 -> INT-18
  - contexte, dependances et references code/docs/ops par implementation
  - sequence d execution et gates de passage
