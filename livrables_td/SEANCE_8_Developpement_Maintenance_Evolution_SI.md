# Séance 8 — Qui développe, maintient et fait évoluer le SI marketing de l'iPhone Duo ?

> **Fil rouge du projet.** Séances 1 à 5 : nous avons analysé Apple, choisi la fonction marketing, modélisé les acteurs, les flux et deux processus BPMN (précommandes du 16/10 et campagne TikTok). Séances 6-7 : nous avons construit le prototype interactif de ce SI. **Séance 8 :** nous identifions les acteurs chargés de **développer**, d'**exploiter** et de **maintenir** ce SI dans la durée, puis ses **perspectives d'évolution numérique**.
>
> *Les organisations internes d'Apple ne sont pas publiques : nous proposons une organisation **réaliste et argumentée**, cohérente avec les pratiques du marché et avec notre dossier. Les chiffres (SLA, budgets) sont des hypothèses de travail.*

---

## 1. Le SI à faire vivre : rappel du périmètre

Le SI marketing du lancement de l'iPhone Duo relie **trois fonctions** (marketing, production, finance) autour d'un **SI partagé** (Fig. 2 du dossier) :

| Brique du SI | Rôle dans le lancement | Exemples de solutions (marché) | Écrans du prototype |
|---|---|---|---|
| **CRM** (relation client) | Compte Apple = identifiant unique ; « Me prévenir », précommandes, consentements | Salesforce, Microsoft Dynamics 365, HubSpot | E24 CRM, E12 Mon compte |
| **ERP** (gestion intégrée) | Stocks, lots de production, coûts de revient, CA prévisionnel, marges | SAP S/4HANA, Oracle | E30, E31, E35, E36 |
| **E-commerce** (apple.com, app Apple Store) | Configurateur, prix et délai affichés, paiement | Plateforme interne d'Apple | E10, E11, E26 |
| **Analytique et écoute sociale** | Trafic, vues, mentions, sentiment | Adobe Analytics, Brandwatch, Talkwalker, Sprinklr | E20, E25 |
| **Gestion des campagnes et de l'influence** | Achat média, influenceurs, appareils de test | TikTok Ads Manager, Meta Ads Manager, Kolsquare, Upfluence | E22, E23, E37, E41 |
| **Pilotage (BI)** | Tableau de bord hebdomadaire, décisions | Tableau, Power BI | E20, E21, E15 |
| **Échanges partenaires (API, EDI)** | Banque/crédit, reprise, opérateurs (eSIM), fournisseurs, régulateurs | API REST, EDI, portails | E42 à E51 |
| **Moteur de processus (BPMN) et bus d'événements** | Orchestration de P1 et P2, notifications entre acteurs | Camunda, Pega, Kafka (exemples) | E02, E03, E04 |

Un SI de ce type n'est jamais « livré une fois pour toutes » : il doit **tenir la charge** le 16 octobre à 14 h (pic de précommandes), **s'adapter** chaque semaine (nouvelles campagnes, nouveaux pays : Inde le 6/11), **rester conforme** (RGPD, DMA) et **être sécurisé**.

---

## 2. Les acteurs du développement et de la maintenance

### 2.1 Vue d'ensemble : la gouvernance du SI

```
                    ┌──────────────────────────────────────────┐
                    │  COMITÉ DE PILOTAGE (direction générale)  │  arbitre budget, priorités, risques
                    └───────────────┬──────────────────────────┘
          ┌─────────────────────────┼──────────────────────────────┐
┌─────────▼─────────┐     ┌─────────▼─────────┐          ┌─────────▼──────────┐
│ MOA : direction   │◄───►│ MOE : DSI (IS&T)   │◄────────►│ Éditeurs, intégrateurs│
│ marketing (+ fin., │     │ architectes, dév., │  contrats │ hébergeurs, TMA       │
│ production)       │     │ exploitation       │  SLA     │ (prestataires)        │
└─────────▲─────────┘     └─────────▲─────────┘          └──────────────────────┘
          │ recette, besoins         │ sécurité, conformité
┌─────────┴─────────┐     ┌─────────┴─────────┐
│ Utilisateurs clés │     │ RSSI, DPO,        │
│ (key users)       │     │ juridique         │
└───────────────────┘     └───────────────────┘
```

La **gouvernance** répartit les décisions entre ceux qui **expriment le besoin** (maîtrise d'ouvrage), ceux qui **construisent et exploitent** (maîtrise d'œuvre) et ceux qui **contrôlent** (sécurité, conformité, finance).

### 2.2 La maîtrise d'ouvrage (MOA) : le « client » du SI

| Acteur | Rôle dans le SI de l'iPhone Duo |
|---|---|
| **Direction marketing iPhone** (sponsor et propriétaire métier) | Porte le besoin : piloter le lancement avant la commercialisation. Fixe les priorités (ex. : tableau de bord hebdomadaire avant le 12/10), valide le budget du projet, prononce la **recette** fonctionnelle. |
| **Finance et production** (MOA associées) | Les processus P1 et P2 traversent leurs couloirs : elles valident les règles de gestion qui les concernent (paiement accepté ?, calcul de la marge et du coût par précommande, stock disponible ?, allongement du délai). |
| **Utilisateurs clés** (*key users*) des équipes e-commerce, data & CRM, réseaux sociaux, Apple Store | Décrivent les besoins concrets, testent les écrans (recette), forment leurs collègues, remontent les anomalies. |
| **Product owner** (méthode agile) | Issu de la direction marketing ou de l'équipe data & CRM : tient le **backlog** (liste priorisée des évolutions) et accepte les livraisons de chaque sprint. |

**Livrables de la MOA :** expression de besoins, cahier des charges fonctionnel (ou *user stories*), règles de gestion, jeux de données de recette, procès-verbal de recette (VABF : vérification d'aptitude au bon fonctionnement).

### 2.3 L'assistance à maîtrise d'ouvrage (AMOA)

Business analysts internes ou cabinet de conseil : ils **traduisent** les besoins métier en spécifications (c'est exactement ce que nous avons fait avec les diagrammes de flux et le BPMN), animent les ateliers, rédigent les cahiers de recette et accompagnent la **conduite du changement** (formation des équipes, guides d'utilisation).

### 2.4 La maîtrise d'œuvre (MOE) : la DSI et ses équipes

Chez Apple, l'informatique interne est assurée par l'organisation **IS&T** (*Information Systems & Technology*), qui joue le rôle de **DSI**.

| Équipe MOE | Responsabilités |
|---|---|
| **Direction de projet / chef de projet SI** | Planning, budget, risques, coordination des prestataires, comités. |
| **Architectes** (entreprise, solution, données) | Choix des briques (CRM, ERP, cloud), intégration par API, modèle de données (identifiant client unique), performance du 16/10. |
| **Équipes de développement** (front e-commerce, back-end, data engineering) | Développent le configurateur, le moteur de délai (tâche P1-T02), les tableaux de bord, les interfaces partenaires. |
| **Équipe data / BI** | Entrepôt de données, indicateurs du § 3.6, tableau de bord hebdomadaire (flux FM-17). |
| **Exploitation (RUN) et SRE** | Mise en production, supervision 24 h/24, gestion de la capacité (montée en charge du 16/10), sauvegardes, plan de reprise. |
| **Centre de services (support N1, N2, N3)** | N1 : assistance aux utilisateurs ; N2 : diagnostic applicatif ; N3 : correction par les développeurs ou l'éditeur. |
| **Qualité et tests** | Tests automatisés (comme nos 66 tests pytest), tests de charge, tests de sécurité. |

### 2.5 Les acteurs externes : éditeurs, intégrateurs, hébergeurs, TMA

| Acteur | Ce qu'il apporte | Exemple pour notre SI |
|---|---|---|
| **Éditeurs de logiciels** | Progiciels et SaaS (licences ou abonnements), correctifs, nouvelles versions | Éditeur du CRM (type Salesforce), de l'ERP (type SAP), de l'écoute sociale (type Brandwatch) |
| **Intégrateurs / ESN** | Paramétrage, développements spécifiques, interfaces (API) entre CRM, ERP et e-commerce | ESN mandatée pour connecter les précommandes au CRM (tâche P1-T06) et à l'ERP (tâches P1-T04, P1-T08) |
| **Hébergeurs / fournisseurs cloud** | Serveurs, stockage, élasticité, réseau de diffusion (CDN) | Centres de données d'Apple et cloud public pour absorber le pic du 16/10 |
| **Prestataire de TMA** | Maintenance applicative sous contrat (voir § 2.6) | Correction et évolution des écrans de pilotage, des interfaces partenaires |
| **Partenaires « fournisseurs de données »** | Flux entrants du diagramme de contexte | Cetelem (FE-09), Likewize (FE-10), opérateurs (FE-02), Samsung Display (FE-04), instituts (FE-08) |

**À retenir :** l'externalisation n'enlève pas la responsabilité. La DSI reste **pilote** des prestataires, à travers des **contrats** et des **SLA**.

### 2.6 La maintenance : TMA et ses quatre formes

La **TMA** (tierce maintenance applicative) confie à un prestataire la maintenance d'une application, pour une durée et à un niveau de service définis.

| Type de maintenance | Définition | Exemple dans notre SI |
|---|---|---|
| **Corrective** | Corriger une anomalie | Le délai affiché ne se met pas à jour après un allongement (tâche P1-T07) |
| **Évolutive** | Ajouter ou modifier une fonctionnalité | Ouvrir les précommandes en Inde le 6/11 (nouveau pays, nouvelle devise) |
| **Adaptative** | Adapter le SI à un changement d'environnement | Nouvelle règle de la CNIL sur les traceurs ; nouvelle version d'iOS ; changement d'API d'un opérateur |
| **Préventive** | Anticiper les problèmes | Test de charge avant le 16/10 ; mise à jour des composants vulnérables |

### 2.7 Les SLA : des engagements mesurables

Un **SLA** (*Service Level Agreement*, accord de niveau de service) fixe des engagements chiffrés, mesurés par des indicateurs, assortis de pénalités. Proposition pour le SI de l'iPhone Duo :

| Engagement | Niveau proposé | Pourquoi |
|---|---|---|
| Disponibilité du configurateur et de la précommande | **99,95 %** sur la semaine du 16/10 (≈ 5 min d'arrêt toléré), 99,9 % le reste de l'année | Le pic de 14 h représente plus de 6 000 précommandes en une heure dans notre base |
| Temps de réponse (prix et délai affichés, P1-T02) | < **1,5 s** pour 95 % des requêtes | Un délai lent fait abandonner le panier |
| Incident bloquant (priorité 1) | prise en charge **15 min**, contournement **2 h**, résolution **4 h**, astreinte 24 h/24 pendant le lancement | Une heure d'arrêt le 16/10 = des milliers de précommandes perdues |
| Incident majeur (P2) / mineur (P3) | résolution **1 jour** ouvré / **5 jours** ouvrés | Hiérarchiser les efforts |
| Fraîcheur du tableau de bord | données de la veille disponibles chaque jour à **8 h** ; tableau hebdomadaire le lundi à **9 h** | Le marketing décide le lundi (§ 6.3) |
| Sauvegarde et reprise | **RPO 5 min** (perte de données maximale), **RTO 1 h** (durée maximale d'interruption) | Ne perdre aucune précommande payée |
| Sécurité | correctif des failles critiques sous **72 h** | Données de paiement et données personnelles |

**Indicateurs de suivi :** taux de disponibilité, MTTR (temps moyen de rétablissement), nombre d'incidents par priorité, respect des délais, satisfaction des utilisateurs. Les SLA se négocient aussi **avec les partenaires** : délai de réponse de l'organisme financier pour une demande de crédit (FE-09R), capacité garantie de Samsung Display (FE-04R).

### 2.8 Sécurité, conformité et contrôle

| Acteur | Rôle |
|---|---|
| **RSSI** (responsable de la sécurité des SI) | Politique de sécurité, gestion des accès (dans notre prototype : contrôle d'accès par rôle — seule la finance peut franchir la passerelle « Paiement accepté ? »), tests d'intrusion, gestion des incidents. |
| **DPO** (délégué à la protection des données) | Registre des traitements, analyses d'impact (AIPD), réponses aux demandes des clients (droit d'accès : bouton « Télécharger mes données » de l'écran E12), relation avec la CNIL. |
| **Juridique et conformité** | Validation des messages publicitaires et des contrats d'influenceurs (flux FI-16 et FI-17), conformité DMA, mentions légales du crédit. |
| **Contrôle de gestion / audit interne** | Suivi du budget du projet (build) et du coût de fonctionnement (run). |

### 2.9 Matrice RACI des principales activités

**R** = réalise · **A** = approuve (rend des comptes) · **C** = consulté · **I** = informé

| Activité | Dir. marketing (MOA) | Finance | Production | DSI (MOE) | Éditeurs / intégrateurs | TMA / exploitation | RSSI / DPO |
|---|---|---|---|---|---|---|---|
| Exprimer le besoin (ex. : tableau de bord hebdomadaire) | **A**, R | C | C | C | I | I | C |
| Modéliser les processus (BPMN P1, P2) | A | R (couloir finance) | R (couloir production) | R | I | I | I |
| Choisir les solutions (CRM, ERP) | C | C | C | **A**, R | C | I | C |
| Développer et intégrer les interfaces (API) | I | I | I | **A** | R | C | C |
| Recette fonctionnelle | **A**, R | R | R | C | C | I | I |
| Mise en production avant le 16/10 | I | I | I | **A**, R | C | R | C |
| Maintenance corrective et évolutive | C | I | I | **A** | C | R | I |
| Gestion des consentements, RGPD | C | I | I | C | C | I | **A**, R |
| Respect des SLA | I | I | I | **A** | R | R | I |

### 2.10 Le cycle de vie du SI : construire, puis faire tourner

1. **Étude d'opportunité** (Séances 1-2) : pourquoi un SI marketing ? → piloter le lancement avant les ventes.
2. **Analyse et modélisation** (Séances 4-5) : acteurs, flux, processus BPMN.
3. **Conception et prototypage** (Séances 6-7) : maquettes interactives, validées avec les utilisateurs.
4. **Développement** en **méthode agile** (sprints de 2 semaines) pour les écrans marketing, et en **cycle en V** pour le paramétrage de l'ERP (plus contraint).
5. **Recette** (tests fonctionnels, tests de charge simulant le 16/10 à 14 h, tests de sécurité).
6. **Mise en production** avec **gel des changements** une semaine avant le 16/10 : plus aucune modification non urgente.
7. **Exploitation et maintenance** (RUN, TMA), mesure des SLA, **amélioration continue**.

**Budget :** on distingue le **build** (construction : licences, intégration, développements) et le **run** (exploitation, TMA, abonnements cloud). Sur la durée de vie d'un SI, le run représente souvent la majorité du **coût total de possession (TCO)**.

### 2.11 Et notre prototype ?

Notre application est déjà conçue comme un « vrai » SI maintenable :

* **un référentiel unique** (`app/referentiel.py`) qui décrit acteurs, flux et processus : une évolution du BPMN se fait à un seul endroit ;
* **66 tests automatisés** (pytest) qui vérifient les processus P1 et P2 de bout en bout, le contrôle des rôles et le calage sur le tableau de bord du 12/10 : c'est le filet de sécurité de la **maintenance corrective** ;
* un **historique Git** (commits) : traçabilité de chaque évolution, retour arrière possible ;
* une **base de démonstration réinitialisable** : utile pour la recette.

---

## 3. Perspectives d'évolution numérique du SI

Notre dossier (§ 7) proposait cinq axes : données en temps réel, IA et prévision, CRM unifié, confidentialité et RGPD, Green IT. Nous les approfondissons ici, technologie par technologie, en partant **des limites observées dans notre prototype**.

### 3.1 IA prédictive : prévoir la demande et détecter les anomalies

* **Constat dans le prototype :** la projection de la demande (écran E21) est une règle simple (« précommandes observées ÷ part normalement atteinte à cette heure »).
* **Évolution :** un modèle de **prévision** (séries temporelles, apprentissage automatique) qui combine les signaux avancés du § 3.6 (visites, « Me prévenir », sentiment, essais en magasin) pour prévoir la demande **par pays, capacité et couleur** — exactement le flux FI-04 vers la production.
* **Autres usages :** détection de **fraude au paiement** (aide à la passerelle P1-G01), score d'**intention d'achat** par segment CRM, détection d'anomalies (pic de commandes de robots revendeurs).
* **Bénéfices :** moins de ruptures (Titane noir), moins de délais allongés, meilleure allocation entre pays (tâche P1-T11).
* **Points de vigilance :** qualité des données, explicabilité de la décision (la passerelle reste une décision **humaine**, comme dans notre maquette), biais.

### 3.2 IA générative : produire et analyser plus vite

* Générer des **variantes** de messages et de visuels pour les campagnes (tests A/B), sous validation du juridique.
* **Synthétiser l'écoute sociale** (« les commentaires négatifs portent surtout sur le prix ») et rédiger le commentaire du tableau de bord hebdomadaire.
* **Assistant** pour le service client AppleCare (pliure de l'écran, eSIM, transfert depuis Android).
* **Cohérence avec la marque :** privilégier le traitement **sur l'appareil** et le **Private Cloud Compute**, argument de confidentialité d'Apple (SWOT, opportunités).
* **Points de vigilance :** erreurs (« hallucinations »), droits d'auteur, transparence envers le public, conformité au **règlement européen sur l'IA**.

### 3.3 ERP, API et architecture orientée événements

* **Constat :** dans le prototype, une précommande payée est visible instantanément par le marketing, la finance et la production grâce à la base partagée et au **bus d'information** (journal des flux).
* **Évolution :** des **API** temps réel entre e-commerce, CRM et ERP, et une **architecture orientée événements** (« précommande payée », « délai allongé », « avis publié ») pour que chaque système réagisse sans ressaisie.
* **API partenaires** : autorisation de crédit (Cetelem), estimation de reprise (Likewize), activation eSIM (opérateurs), capacités (Samsung Display) — aujourd'hui simulées par nos portails E42 à E51.
* **CRM unifié** (dossier § 7) : relier les données en ligne, en magasin et chez les opérateurs autour du compte Apple.

### 3.4 Cloud : absorber le pic et partager la donnée

* **Élasticité** : multiplier automatiquement les serveurs le 16/10 à 14 h, puis les réduire (on ne paie que ce qu'on consomme).
* **SaaS** pour certaines briques (CRM, écoute sociale), **plateforme de données** (lac de données) pour croiser ventes, campagnes et écoute sociale.
* **Points de vigilance :** dépendance au fournisseur, localisation des données (transferts hors UE et RGPD), maîtrise des coûts (FinOps), empreinte énergétique (**Green IT**, cohérent avec l'objectif de neutralité carbone 2030 d'Apple).

### 3.5 IoT : de nouvelles sources de données

* **Magasins connectés :** capteurs de fréquentation et appareils de démonstration connectés → mesure plus fine des essais (flux FM-16).
* **Supply chain :** traçabilité des lots (RFID, capteurs) → date de disponibilité plus fiable, donc **délai affiché** plus juste (P1-T02).
* **Appareils eux-mêmes :** événements d'activation eSIM, statistiques d'usage **anonymisées et soumises au consentement** → mesurer la satisfaction réelle et les usages du pliable.

### 3.6 Automatisation (RPA et workflows)

* **RPA** (robots logiciels) pour les tâches répétitives sans API : consolider les rapports des agences (FE-07R) et les ventes des revendeurs (FE-03R), rapprocher les paiements.
* **Moteur de workflow BPMN** (comme celui de notre prototype) : les tâches automatisées (P1-T02, T04, T05, T06, T09) s'exécutent seules ; les humains se concentrent sur les décisions (passerelles).
* **Automatiser le tableau de bord hebdomadaire** (FM-17) chaque lundi à 9 h, avec alertes quand un indicateur passe « en retard ».

### 3.7 Cybersécurité et RGPD : la confiance comme fondation

* **Sécurité :** authentification forte (MFA), principe du moindre privilège (contrôle par rôle, déjà dans la maquette), chiffrement, approche **zero trust**, protection contre les robots qui accaparent les précommandes, plan de continuité (PCA/PRA) pour le jour J, directive européenne **NIS2**.
* **RGPD :** consentement explicite (case « Me prévenir », bandeau cookies de la maquette), **minimisation** et **pseudonymisation** (identifiants masqués dans le CRM du prototype), registre des traitements et analyse d'impact (flux FE-11A), exercice des droits (export des données, écran E12).
* **DMA :** conséquences pour l'App Store et l'interopérabilité ; fonctionnalités différées dans l'UE à documenter clairement (limite relevée en Séance 3).

### 3.8 Feuille de route proposée

| Horizon | Évolution | Valeur | Complexité | Acteurs principaux |
|---|---|---|---|---|
| **Court terme** (novembre 2026) | Ouverture Inde : nouveau pays, nouvelle devise, plan de lancement (FI-02) | Élevée | Faible | MOA marketing, TMA (évolutive) |
| Court terme | Automatisation du tableau de bord hebdomadaire et alertes | Élevée | Faible | Équipe data, DSI |
| **Moyen terme** (2027) | API temps réel CRM ↔ ERP ↔ partenaires (crédit, reprise, opérateurs) | Élevée | Moyenne | Architectes, intégrateur |
| Moyen terme | Prévision de la demande par IA (pays × couleur) | Élevée | Moyenne | Data, production, finance |
| Moyen terme | IA générative pour les variantes de campagnes et le SAV | Moyenne | Moyenne | Marketing, juridique, DPO |
| **Long terme** | CRM unifié en ligne / magasin / opérateurs ; magasins et supply chain connectés (IoT) | Élevée | Élevée | Comité de pilotage, DSI |
| En continu | Cybersécurité, RGPD, Green IT, FinOps | Indispensable | Continue | RSSI, DPO, DSI |

---

## 4. Conclusion de la Séance 8

Un SI performant n'est pas seulement un ensemble d'outils : c'est une **organisation**. La **MOA** (direction marketing, avec la finance et la production) exprime et valide les besoins ; la **MOE** (DSI, architectes, développeurs, exploitation) construit et fait fonctionner ; les **éditeurs, intégrateurs et prestataires de TMA** apportent leur expertise sous le contrôle de **SLA** mesurables ; le **RSSI** et le **DPO** garantissent la sécurité et la conformité. Les évolutions numériques — **IA prédictive et générative, API et événements, cloud, IoT, automatisation, cybersécurité** — prolongent directement notre problématique : **mieux piloter un lancement avant même la commercialisation**, avec des données plus rapides, plus fiables et mieux protégées.
