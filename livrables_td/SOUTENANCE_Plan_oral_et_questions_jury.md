# Soutenance — plan de l'oral (10 minutes) et questions du jury (5 minutes)

**Sujet :** le système d'information marketing d'Apple pour le lancement de l'iPhone Duo.
**Problématique :** *en quoi le SI marketing d'Apple lui permet-il de piloter et d'évaluer le lancement de l'iPhone Duo avant même sa commercialisation ?*

**Répartition proposée (4 orateurs) :** A = introduction et entreprise · B = fonction marketing, stratégie digitale, flux · C = processus BPMN et prototype · D = démonstration, Séance 8, conclusion. *Adaptez les lettres aux prénoms du groupe.*

**Règle d'or :** une idée par diapositive, un visuel par diapositive (les captures sont dans `livrables_td/captures/`, les figures du dossier dans `livrables_td/figures/`). Le prototype est lancé **avant** la soutenance (double-clic sur `lancer_app.command`), horloge réglée sur « Précommandes J+3 », **mode Pas à pas**.

---

## Déroulé minuté

| # | Diapositive | Durée | Orateur |
|---|---|---|---|
| 1 | Titre | 0:00 – 0:15 | A |
| 2 | Problématique et fil rouge | 0:15 – 0:55 | A |
| 3 | Apple et l'iPhone Duo : chiffres clés et SWOT ciblé | 0:55 – 1:50 | A |
| 4 | Pourquoi la fonction marketing ? | 1:50 – 2:40 | B |
| 5 | Stratégie digitale : du site et de TikTok aux données | 2:40 – 3:20 | B |
| 6 | Acteurs et flux d'information | 3:20 – 4:15 | B |
| 7 | BPMN P1 : les précommandes du 16 octobre | 4:15 – 5:00 | C |
| 8 | BPMN P2 : la campagne TikTok | 5:00 – 5:35 | C |
| 9 | Notre prototype : un SI qui exécute nos modèles | 5:35 – 6:15 | C |
| 10 | Démonstration en direct | 6:15 – 8:00 | D (C au clavier) |
| 11 | Le tableau de bord : décider avant les ventes | 8:00 – 8:30 | D |
| 12 | Séance 8 : qui fait vivre le SI, et demain ? | 8:30 – 9:30 | D |
| 13 | Conclusion : réponse à la problématique | 9:30 – 10:00 | A |

---

## Diapositive par diapositive

### 1. Titre (15 s) — A
* **Contenu :** « Le système d'information marketing d'Apple — le lancement de l'iPhone Duo ». Noms, TD, enseignant(e), année 2026-2027.
* **Visuel :** `captures/E10_client_produit.png` (page produit) en fond, ou l'illustration du pliable de l'accueil.
* **À dire :** « Bonjour, nous allons vous montrer comment un système d'information permet de piloter le lancement d'un produit… avant même qu'il soit en vente. »

### 2. Problématique et fil rouge (40 s) — A
* **Contenu :** l'iPhone Duo, premier iPhone pliable : keynote le 9/09, précommandes le 16/10 à 14 h, sortie le 23/10, à partir de 2 339 €. **Problème :** pas encore de chiffre de ventes → comment savoir si la communication fonctionne ? Fil rouge : Séances 1-2 (entreprise, fonction) → 3 (digital) → 4-5 (flux, BPMN) → 6-7 (prototype) → 8 (maintenance, évolutions).
* **Visuel :** frise de l'accueil (`captures/E00_transversal_accueil.png`, zone de la frise).
* **Message clé :** le SI doit capter des **signaux avancés** (visites, inscriptions, sentiment, essais) puis les **précommandes**.
* **Transition :** « Pour comprendre ce besoin, il faut d'abord comprendre Apple. »

### 3. Apple et l'iPhone Duo : chiffres clés et SWOT ciblé (55 s) — A
* **Contenu :** 416 Md$ de CA en 2025 (iPhone ≈ 50 %, services ≈ 26 %), 2,5 milliards d'appareils actifs, 166 000 salariés, 532 Apple Store. SWOT **ciblé sur le lancement** : forces (marque, écosystème, fidélité, données du parc) ; faiblesses (dépendance à l'iPhone, **Samsung Display fournisseur unique de l'écran**) ; opportunités (nouvelle catégorie, reprise, paiement en plusieurs fois) ; menaces (**prix**, flambée de la mémoire, concurrents déjà installés, DMA).
* **Visuel :** matrice SWOT en 4 cases, 2 éléments par case maximum.
* **Message clé :** atouts marketing exceptionnels, mais un produit très cher, attendu par des concurrents déjà présents → il faut **mesurer vite** si le message passe.

### 4. Pourquoi la fonction marketing ? (50 s) — B
* **Contenu :** rôles (image premium, lancement des nouvelles catégories, services, différenciation sur la confidentialité) ; interactions **production** (volumes, Samsung Display) et **finance** (prix, budget, marge) ; outils : **CRM** (compte Apple = identifiant unique), **ERP**, analytique, écoute sociale, BI.
* **Visuel :** triangle marketing – production – finance (`figures/Fig2_flux_internes.png`).
* **Message clé :** le marketing ne peut rien promettre sans la production et la finance → le SI doit être **partagé**.

### 5. Stratégie digitale (40 s) — B
* **Contenu :** site apple.com (informer, rassurer, convertir : charnière en titane, reprise, paiement en 10 fois, onglet « passer d'Android ») ; TikTok (usages humoristiques : yoga, café, cinéma de poche ; influenceurs). **Chaque visite, inscription, vue, commentaire devient une donnée pour le SI.**
* **Visuel :** `captures/E10_client_produit.png` + une vidéo du fil TikTok (`captures/E23_mkt_social_campagne.png`).
* **Limite relevée :** restrictions européennes (Siri IA) reléguées en notes de bas de page ; prix jamais évoqué sur TikTok.

### 6. Acteurs et flux d'information (55 s) — B
* **Contenu :** 12 acteurs externes (diagramme de contexte), 8 acteurs internes, 3 niveaux de modèles (Fig. 1 contexte, Fig. 2 flux internes, Fig. 3 flux marketing). **Apport du prototype : chaque flèche a reçu un code** (FE = externe, FI = interne, FM = marketing) : 54 flux issus de nos figures + 6 compléments = 60 flux codifiés.
* **Visuel :** `captures/E01_transversal_flux.png` (cartographie interactive, épaisseur = volume réel).
* **Message clé :** l'équipe **data et CRM est le centre du système** (elle reçoit tout et produit le tableau de bord hebdomadaire).

### 7. BPMN P1 : les précommandes du 16 octobre (45 s) — C
* **Contenu :** 4 couloirs (client, marketing, finance, production) ; 3 passerelles = 3 **règles de gestion** : *Paiement accepté ?* (finance, avec la réponse de l'organisme financier), *Stock disponible ?* (production → sinon allonger le délai), *Demande supérieure à l'offre ?* (marketing → hausse de production ou relance de la communication).
* **Visuel :** `captures/E02_transversal_processus-P1.png` (BPMN vivant avec jetons).
* **Message clé :** une précommande enregistrée est **immédiatement** visible par le marketing, la finance et la production.

### 8. BPMN P2 : la campagne TikTok (35 s) — C
* **Contenu :** même une campagne de communication mobilise la **finance** (budget, coût d'acquisition) et la **production** (appareils de test, plan de production). Une **boucle** : mesurer → objectifs atteints ? non → ajuster → mesurer.
* **Visuel :** `captures/E03_transversal_processus-P2.png`.
* **Anecdote utile :** en codant le processus, nous avons découvert un flux absent de notre Fig. 2 : la **demande d'appareils de test** du marketing à la production (FI-13). Le prototype a **amélioré nos modèles**.

### 9. Notre prototype : un SI qui exécute nos modèles (40 s) — C
* **Contenu :** application web (FastAPI, SQLite, fonctionne hors-ligne). Quatre principes : (1) un **référentiel unique** issu des Séances 1-5 ; (2) un **moteur BPMN** à jetons ; (3) un **bus d'information** : chaque action émet un flux codifié et notifie le destinataire ; (4) un **contrôle d'accès par rôle** : seule la finance franchit « Paiement accepté ? ». Base pré-remplie : 120 000 inscrits « Me prévenir », 38 000 précommandes en France, calée sur notre tableau de bord du 12/10. 25 « vues acteur », 41 écrans, 21 tests automatisés.
* **Visuel :** `captures/E00_transversal_accueil.png` (grille des acteurs) ou schéma d'architecture simple.

### 10. Démonstration en direct (1 min 45) — D (C au clavier)
Scénario **testé**, clic par clic (voir aussi `GUIDE_DEMO_Soutenance.md`) :
1. **Vue Client** → *Configurer et précommander* : 512 Go Titane noir, reprise d'un iPhone 13 Pro, paiement en 10 fois → le délai affiché est calculé **en direct** à partir du stock (tâche T02) → *Valider*. *(20 s)*
2. **Vue Finance** → la précommande est dans la file → *Accepter* : CA prévisionnel et marge enregistrés (T04, T05), CRM mis à jour (T06), production notifiée. *(20 s)*
3. **Vue Production** → *Vérifier le stock* : Titane noir en rupture pour le 23/10 → *Allonger le délai affiché* → *Réserver*. Le client reçoit sa confirmation. *(25 s)*
4. Touche **I** : **mode Inspection** → on voit sur l'écran quelles tâches BPMN et quels flux sont illustrés. *(15 s)*
5. **Processus P1** : la précommande a avancé de couloir en couloir (cliquer sur l'instance pour tracer son parcours). *(25 s)*
* **Plan B** si le réseau ou l'ordinateur pose problème : les captures `captures/E11…`, `E30…`, `E35…` et `E02…` sur les diapositives suivantes.

### 11. Le tableau de bord : décider avant les ventes (30 s) — D
* **Contenu :** le lundi 12/10, 4 objectifs sur 7 atteints : beaucoup de curiosité (2,35 M de visites, 31 M de vues TikTok, 17 200 essais) mais une intention d'achat en retard (6 % pour 8 %) et des commentaires négatifs sur le **prix**. Décision : mettre en avant la **reprise** et le **paiement en 10 fois** → 120 000 inscrits à l'ouverture. Puis à J+1 : demande projetée 1,28 × l'offre en France → transfert de 3 000 unités depuis l'Allemagne.
* **Visuel :** `captures/E25_mkt_data_mesure.png` (tableau du § 6.3) et `captures/E21_dir_marketing_pilotage-precommandes.png`.
* **Message clé :** **c'est la réponse à la problématique** : le SI permet d'agir avant le 16/10, puis pendant les précommandes.

### 12. Séance 8 : qui fait vivre le SI, et demain ? (1 min) — D
* **Contenu :** **MOA** = direction marketing (+ finance, production) ; **MOE** = DSI d'Apple (IS&T), architectes, développeurs, exploitation ; **éditeurs** (CRM, ERP) et **intégrateurs** ; **TMA** (corrective, évolutive, adaptative, préventive) ; **SLA** : 99,95 % de disponibilité la semaine du 16/10, incident bloquant résolu en 4 h. Évolutions : **IA prédictive** (demande par pays et couleur), **IA générative** (variantes de campagnes, SAV), **API** temps réel, **cloud** élastique pour le pic de 14 h, **IoT** (magasins, supply chain), **RPA**, **cybersécurité et RGPD**.
* **Visuel :** tableau RACI simplifié + feuille de route (court / moyen / long terme).

### 13. Conclusion (30 s) — A
* **Réponse à la problématique :** le SI marketing permet de piloter le lancement avant la commercialisation **parce qu'il relie** les signaux avancés (site, TikTok, magasins) aux décisions de la finance et de la production, **dans des processus partagés**.
* **Limites :** données fictives (calées sur le dossier), intégrations partenaires simulées, pas de test de charge réel.
* **Ouverture :** le prix reste le principal frein : le SI le **révèle**, mais ce sont des **décisions marketing et financières** qui y répondent.
* **Phrase finale :** « Merci de votre attention, nous sommes prêts pour vos questions. »

### Diapositives d'annexe (pour les questions)
RACI détaillé, tableau des SLA, matrice de traçabilité (tâches BPMN ↔ écrans), liste des 60 flux, glossaire. *Elles ne sont pas présentées, mais permettent de répondre avec un visuel.*

---

## Les 15 questions pièges du jury… et leurs réponses

**1. Quelle est la différence entre un système d'information et un système informatique ?**
Le **système d'information** est l'ensemble organisé des ressources (personnes, procédures, données, outils) qui collectent, stockent, traitent et diffusent l'information utile à l'organisation. Le **système informatique** n'en est que la partie technique (matériels, logiciels, réseaux). Exemple : la décision de la directrice marketing le lundi 12/10, prise à partir du tableau de bord, fait partie du SI ; le serveur qui calcule le tableau de bord fait partie du système informatique.

**2. Pourquoi la fonction marketing, alors que la production semble plus critique (pénurie d'écrans) ?**
Parce que **le marketing est au cœur du modèle d'Apple** (marque, fidélité, écosystème) et que le lancement d'une nouvelle catégorie exige de **créer le désir avant la vente**. Mais nous n'avons pas ignoré la production : nos schémas sont construits sur le **triangle marketing – production – finance**, et la contrainte Samsung Display apparaît dans nos flux (FE-04), dans le BPMN (*Stock disponible ?*) et dans le prototype (capacité qui limite la hausse de production).

**3. Comment être sûr que vos « signaux avancés » prédisent vraiment les ventes ?**
On ne l'est pas a priori : c'est pourquoi le SI **compare** ensuite les signaux aux précommandes (taux de conversion visite → précommande, part des clients venant d'Android) puis aux ventes. Notre SWOT et notre tableau de bord montrent d'ailleurs un **écart** : beaucoup de curiosité, moins d'intention d'achat. L'évolution proposée en Séance 8 est un **modèle de prévision** calibré sur ces historiques.

**4. Pourquoi la passerelle « Paiement accepté ? » est-elle dans le couloir Finance et pas chez la banque ?**
La banque (organisme financier) est un **acteur externe** : elle n'est pas un couloir de notre processus interne mais un émetteur de flux (FE-09 : demande de crédit / accord). La décision d'accepter le paiement reste une **règle interne** de la finance d'Apple, qui s'appuie sur la réponse de la banque. Dans le prototype, la finance ne peut pas valider tant que la réponse FE-09R n'est pas arrivée.

**5. Dans votre BPMN, « Analyse le tableau de bord » est déclenchée après chaque précommande. Est-ce réaliste ?**
Non, et le prototype nous l'a montré : nous l'avons implémentée comme une **tâche par lot** — une analyse regroupe toutes les précommandes en attente (les « jetons » s'accumulent sur la tâche). Pour être plus rigoureux en BPMN, on utiliserait un **événement intermédiaire temporel** (« chaque lundi à 9 h ») ou un **sous-processus** de pilotage. C'est une piste d'amélioration du modèle.

**6. Quelle différence entre votre diagramme de contexte et votre diagramme des flux internes ?**
Le **diagramme de contexte** représente le système (le SI marketing) comme une boîte noire et ses échanges avec l'**environnement** (12 acteurs externes). Le **diagramme des flux internes** ouvre la boîte : il montre les échanges entre **acteurs internes** (direction générale, marketing, finance, production, SI partagé). La Fig. 3 descend encore d'un niveau, dans la direction marketing.

**7. Les concurrents sont reliés en pointillés : pourquoi les représenter s'il n'y a aucun échange ?**
Parce que l'information existe : Apple **observe** les prix et produits concurrents (veille). Ce flux est **indirect** : il n'y a pas d'émetteur volontaire. C'est pourquoi le prototype ne propose pas d'interface « concurrent » : l'écran de veille est celui de l'**équipe data d'Apple**.

**8. Vos données sont-elles réelles ?**
Les données sur l'**entreprise** viennent de sources réelles (Xerfi Global, résultats publiés par Apple, presse spécialisée), citées dans le dossier. Les données **du SI** (clients, précommandes, campagnes) sont **fictives**, comme l'annonce notre dossier, mais **cohérentes** : la base est calée pour reproduire exactement notre tableau de bord du 12/10 (2 350 000 visites, 96 000 inscriptions, 31 M de vues…). Les identifiants clients sont en plus **pseudonymisés** à l'affichage.

**9. Votre prototype est-il un vrai SI ou une maquette ?**
C'est une **maquette haute fidélité exécutable** : les processus s'exécutent réellement (moteur BPMN, règles de gestion, base de données, contrôle des rôles, 21 tests automatisés). Mais ce n'est pas un SI de production : pas d'authentification réelle, pas de test de charge, intégrations partenaires simulées. Il sert à **valider les besoins** avec les utilisateurs avant de développer — c'est le rôle du prototypage dans un projet SI.

**10. Quelle est la différence entre MOA et MOE ? Qui est la MOA ici ?**
La **MOA** (maîtrise d'ouvrage) exprime le besoin, finance et valide (recette) : c'est la **direction marketing iPhone**, avec la finance et la production pour leurs couloirs. La **MOE** (maîtrise d'œuvre) conçoit, réalise et exploite : la **DSI** (IS&T chez Apple), avec ses architectes, développeurs et équipes d'exploitation, ainsi que les intégrateurs. L'**AMOA** aide la MOA à formaliser ses besoins — ce que nous avons fait avec nos diagrammes.

**11. Qu'est-ce qu'un SLA ? Donnez un exemple chiffré.**
Un **accord de niveau de service** : un engagement mesurable d'un prestataire, assorti de pénalités. Exemple : disponibilité du site de précommande de **99,95 %** pendant la semaine du 16/10, temps d'affichage du prix et du délai inférieur à **1,5 s** pour 95 % des requêtes, incident bloquant **résolu en 4 heures** avec astreinte 24 h/24.

**12. Comment votre SI respecte-t-il le RGPD ?**
Par la **conception** : consentement explicite (case non pré-cochée pour « Me prévenir », bandeau cookies avec « Refuser »), **minimisation** (seuls les clients consentants sont ciblables dans le CRM), **pseudonymisation** des identifiants à l'affichage, **droit d'accès** (export des données dans « Mon compte »), **registre des traitements** et **analyse d'impact** transmis à la CNIL (flux FE-11A). Le DPO en est garant (Séance 8).

**13. CRM ou ERP : lequel est le plus important pour le marketing ?**
Les deux sont **complémentaires**. Le **CRM** connaît le client (compte Apple, appareil actuel, inscription « Me prévenir », consentements) : il sert au **ciblage**. L'**ERP** connaît les stocks, les coûts et le chiffre d'affaires : il conditionne le **délai affiché** et la **marge**. Notre Fig. 2 et notre prototype montrent qu'il faut un **SI partagé** : sans ERP, le marketing promettrait des délais impossibles.

**14. Si la demande dépasse l'offre, pourquoi ne pas simplement augmenter le prix ?**
Parce que le prix est un **arbitrage marketing – finance** (§ 3.4) : un iPhone Duo déjà à 2 339 € rencontre un frein prix (commentaires négatifs, intention d'achat en retard). Augmenter le prix pénaliserait l'image et la conquête des utilisateurs Android. Le SI propose d'autres leviers : **transférer** des stocks entre pays, **augmenter** la production dans la limite de la capacité de Samsung Display, **allonger le délai** de façon transparente. Le pouvoir de fixation des prix d'Apple (SWOT) sert plutôt à **absorber** la hausse du coût de la mémoire.

**15. Si vous ne deviez financer qu'une seule évolution du SI, laquelle ?**
La **prévision de la demande par IA** (pays × couleur), car elle agit sur le problème le plus coûteux observé dans notre prototype : les **délais allongés** sur le Titane noir et les transferts d'urgence entre pays. Elle s'appuie sur des données que le SI collecte déjà (signaux avancés, précommandes) et réduit à la fois les ruptures (marketing), les coûts logistiques (production) et le coût d'acquisition (finance). À court terme et pour un coût faible, nous automatiserions d'abord le **tableau de bord hebdomadaire**.

### Questions bonus (si le jury creuse)
* **« Pourquoi le flux FI-13 n'apparaît-il pas dans votre Fig. 2 ? »** — Parce que nous l'avons découvert en codant le BPMN P2 : la tâche « Fournit les appareils de test » suppose une demande du marketing à la production. Le prototypage sert aussi à **valider et corriger** les modèles.
* **« Que se passe-t-il si l'organisme financier refuse le crédit ? »** — La finance refuse le paiement : branche « non » de la passerelle, retour à la tâche « Choisit sa configuration » ; le client est notifié et peut choisir un autre moyen de paiement (démontrable avec l'option « simuler un refus »).
* **« Pourquoi SQLite et pas un vrai SGBD ? »** — Pour un prototype hors-ligne installable en un double-clic, SQLite suffit (une base de 60 000 précommandes y tient sans difficulté) ; en production on utiliserait un SGBD serveur ou les bases du CRM et de l'ERP.

---

## Conseils pour le jour J
* **Répéter avec un chronomètre** : la démonstration est le moment le plus risqué ; la faire à deux (un qui parle, un qui clique).
* **Réinitialiser la base** juste avant de passer (menu horloge → « Réinitialiser la base de démonstration »), puis régler l'horloge sur « Précommandes J+3 ».
* **Prévoir le plan B** : captures intégrées aux diapositives, au cas où.
* **Répondre en reliant aux séances** : « comme nous l'avons montré en Séance 4… », c'est ce qui prouve la cohérence du projet.
* **Ne jamais affirmer qu'une donnée fictive est réelle** : dire « dans notre simulation, calée sur notre tableau de bord ».
