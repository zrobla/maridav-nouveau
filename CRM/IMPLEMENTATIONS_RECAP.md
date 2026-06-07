# Recap Implementations CRM + FNE (Maridav CI)

Date: 2026-03-05  
Contexte: socle MVP PREMIUM Ventes/FNE dans le CRM Django Maridav CI.

## INT-01 - Ventes Express + Facturation CRM
- Statut: done
- Implémenté:
  - cycle facture complet (création, édition, impression, lignes produits)
  - attribution automatique du commercial responsable (fallback Maridav)
  - flux UI + API pour commandes/factures
- Use cases:
  - vente comptoir immédiate sans passage par site web
  - émission rapide de facture en agence/terrain
  - suivi portefeuille commercial par vendeur

## INT-02 - Profil fiscal client obligatoire
- Statut: done
- Implémenté:
  - champs fiscaux client (NCC, NTD, RCCM, régime)
  - validations de prérequis avant émission facture
- Use cases:
  - conformité fiscale minimale avant certification FNE
  - réduction des rejets FNE liés à données client incomplètes

## INT-03 - Connecteur FNE outbound
- Statut: done
- Implémenté:
  - génération d’événements outbox facture vers connecteur FNE
  - mapping champs facture vers payload FNE
  - idempotence et retry/dlq via moteur connecteurs enterprise
- Use cases:
  - envoi automatique des factures émises au flux FNE
  - traçabilité des transmissions et reprise sur incident

## INT-04 - Connecteur FNE inbound
- Statut: done
- Implémenté:
  - ingestion des retours FNE (pending/certified/rejected)
  - mise à jour automatique `fne_status`, `fne_reference`, erreurs
- Use cases:
  - suivi en temps réel du statut fiscal de chaque facture
  - pilotage opérationnel sur les rejets FNE

## INT-05 - Gate de conformité opérationnelle
- Statut: done
- Implémenté:
  - blocage livraison commande si factures non certifiées FNE
  - enforcement en UI, API et inbound ERP/logistique
- Use cases:
  - empêcher toute exécution aval non conforme
  - sécuriser livraison/compta vis-à-vis de la réglementation

## INT-06 - Workflow d’avoir / annulation conforme
- Statut: done
- Implémenté:
  - nature facture (standard/avoir)
  - lien facture d’origine obligatoire pour avoir
  - règles métier (source émise + certifiée FNE)
  - action UI “Créer avoir” et auto-annulation source en avoir intégral
- Use cases:
  - correction post-facturation sans rupture de traçabilité
  - gestion des annulations alignée conformité FNE

## INT-07 - Réconciliation paiements
- Statut: done
- Implémenté:
  - ledger `InvoicePayment` (espèces, mobile money, virement, chèque, crédit)
  - recalcul automatique `paid_amount` et statut facture
  - écrans CRM de saisie paiement + historique
  - endpoint API `/api/v1/invoice-payments/`
  - inbound `payment.sync` idempotent depuis connecteur enterprise
- Use cases:
  - encaissement multi-canal et suivi reste à payer
  - rapprochement automatique facture/paiement
  - synchronisation paiements reçus depuis ERP/fintech

## INT-08 - Connecteur ERP/Compta (finance)
- Statut: done
- Implémenté:
  - flux outbox dédié `invoice_payment.created|updated|deleted`
  - payload paiement standardisé vers ERP/BI
  - mappings seedés pour `invoice_payment` et `inbox:payment.sync`
- Use cases:
  - suppression de la ressaisie comptable côté finance
  - alimenter BI avec cash-in réel par facture
  - alignement temps réel CRM <-> ERP/Compta

## INT-09 - Gouvernance qualité + observabilité finance
- Statut: done
- Implémenté:
  - contrôles data quality facture/paiements (mismatch ledger, mode de paiement manquant)
  - auto-résolution des anomalies devenues obsolètes après correction
  - métriques observabilité finance (anomalies ouvertes, impayés échus, rejets FNE)
  - alertes dédiées `finance_*` dans la synthèse observabilité
- Use cases:
  - détecter immédiatement les écarts de réconciliation avant clôture
  - prioriser le traitement des factures rejetées FNE
  - piloter le risque cash et conformité depuis un seul cockpit

## INT-10 - Industrialisation MVP neutre (core reusable)
- Statut: done
- Implémenté:
  - couche tenant `crm/services/tenant.py` pour neutraliser branding/identité CRM par configuration
  - injection globale `crm_branding` via context processor Django
  - interface CRM (`templates/base.html`) rendue multi-tenant sans hardcode Maridav
  - `build_packplus_client_kit` enrichi avec `tenant_profile.json` + variables env tenant/cookies
  - manifest kit enrichi avec profil tenant pour réplication client par client
- Use cases:
  - déployer le même noyau CRM/FNE chez une autre entreprise sans fork du code
  - livrer un kit onboarding prêt pour configuration rapide (domaines, branding, cookies)
  - conserver Maridav comme tenant 1 tout en productisant la base pour le marché

## Valeur business immédiate
- Exécution vente -> facture -> conformité FNE -> paiement -> synchronisation finance sans cassure.
- Traçabilité forte (audit + outbox/inbox + statuts).
- Base industrialisée et neutralisée pour duplication multi-entreprises en Côte d Ivoire.
