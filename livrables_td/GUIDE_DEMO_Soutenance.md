# Guide de démonstration du prototype (soutenance)

Ce guide permet de **rejouer en direct**, en moins de deux minutes, les processus de nos Séances 4 et 5 dans le prototype. Chaque étape a été testée par un script qui clique réellement dans l'application.

## Avant de passer (5 minutes avant)

1. Double-cliquer sur **`lancer_app.command`** : le navigateur s'ouvre sur http://localhost:8005.
2. Cliquer sur l'**horloge** (en haut à droite) → **« Réinitialiser la base de démonstration »** (efface les essais de répétition).
3. Toujours dans l'horloge : choisir **« Précommandes J+3 — lun. 19 oct. 2026, 10:00 »**, exécution **« Pas à pas »**, vitesse **« Pause »** (l'heure ne bouge plus pendant l'oral).
4. Agrandir la fenêtre (plein écran) et zoomer à 90 % si le vidéoprojecteur est en 1280 px.
5. Ouvrir un second onglet sur **Processus P1** (http://localhost:8005/processus/P1) pour la fin de la démonstration.

**Raccourcis :** **A** = changer de vue acteur · **I** = mode inspection · **Échap** = fermer un menu.

## Scénario principal : une précommande traverse les quatre couloirs du BPMN P1

| # | Vue acteur | Action | Ce qu'il faut dire | Tâches / flux |
|---|---|---|---|---|
| 1 | **Client** → *Configurer et précommander* | Garder 512 Go Titane noir, reprise d'un iPhone 13 Pro, paiement en 10 fois → **Valider la précommande** | « Le délai affiché est calculé en direct par le SI à partir du stock de l'ERP : c'est la tâche T02, automatisée. » | P1-T01, T02, T03 · FE-01R, FE-10, FE-09A |
| 2 | Bouton **« Passer à la vue Finance »** | Dans la file *Paiements à vérifier* : **Accepter** | « La finance franchit la passerelle *Paiement accepté ?* ; le SI enregistre aussitôt le CA prévisionnel, la marge et met à jour le CRM. » | P1-G01, T04, T05, T06 · FI-12, FM-19 |
| 3 | **Production** → *Stocks et réservations* | **Vérifier le stock** → **Allonger le délai affiché** → **Réserver l'appareil** | « Le Titane noir est en rupture pour le 23/10 : c'est la branche *non* de *Stock disponible ?*. Le client reçoit la nouvelle date. » | P1-G02, T07, T08, T09 · FI-11, FI-05, FE-01A |
| 4 | Touche **I** | Montrer le tiroir d'inspection | « Chaque écran indique quelles tâches BPMN et quels flux de nos séances il illustre. » | — |
| 5 | Onglet **Processus P1** | Cliquer sur l'instance la plus récente | « Le jeton a parcouru tout le diagramme de notre Fig. 4. » | E02 |

**Variante si le jury demande « et si le paiement est refusé ? »** : à l'étape 1, cocher *« simuler un refus de la banque »* ; à l'étape 2, cliquer **Refuser** → le client voit « Paiement refusé — Modifier ma configuration » (retour à T01).

**Variante crédit :** choisir 2 To + financement 24 mois (> 3 000 €) → la demande part en **étude** chez l'organisme financier (vue *Organismes financiers* → *Décider* → *Accorder*), puis la finance peut valider.

## Scénario complémentaire : décider avec le tableau de bord (30 s)

1. **Direction marketing** → *Analyse des précommandes* : la France affiche **Demande > offre**.
2. **Analyser** (tâche T10) → **Oui → demander à la production** (G03).
3. **Production** → *Plan de production* → **Exécuter (T11)** : transfert depuis l'Allemagne et hausse hebdomadaire, dans la limite de la capacité de Samsung Display (essayer une hausse énorme : le SI la refuse).

## Scénario P2 (si le jury veut voir la campagne)

1. **Direction marketing** → *Campagne et consignes* → **Nouvelle campagne** → **Proposer à la finance**.
2. **Finance** → *Budgets, prix et CAC* → **Accorder le budget** (ou *Non : revoir* pour montrer la boucle).
3. **Réseaux sociaux** → **Publier sur TikTok** → cocher 2 influenceurs → **Sélectionner**.
4. **Production** → *Appareils de test* → **Expédier**.
5. **Influenceurs & médias** → **Publier mon avis** (deux fois).
6. **Data & CRM** → *Mesure* → **Mesurer maintenant** → **Direction marketing** → **Non : ajuster** → **Réseaux sociaux** → **Ajuster** → nouvelle mesure → **Oui : atteints** → **Envoyer rapport et prévisions**.
7. **Production** → **Ajuster le plan** ; **Finance** → **Calculer le coût d'acquisition** → le processus atteint l'événement **Fin**.

*Astuce : la pastille noire en bas à gauche (« tâches en attente ») indique à chaque instant quelle vue acteur doit agir : un clic y emmène directement.*

## Rejouer le temps

| Préréglage de l'horloge | À montrer |
|---|---|
| Keynote — 9 sept. 19:00 | Début du processus P2 ; configurateur fermé, « Me prévenir » ouvert |
| Tableau de bord — 12 oct. 09:00 | Le tableau du § 6.3 à l'identique (*Mesure et tableau de bord*) ; la campagne de lancement attend la décision « Objectifs atteints ? » |
| Ouverture — 16 oct. 14:00 (vitesse × 60) | Les précommandes arrivent en direct (cockpit, onglet *Précommandes*) |
| J+3 — 19 oct. 10:00 | Files d'attente de chaque acteur (démonstration principale) |
| Après la sortie — 2 nov. 10:00 | Indicateurs de résultat : livraisons, satisfaction, retours, part de marché |

## Plan B
Si l'ordinateur ou l'application pose problème, utiliser les captures de `livrables_td/captures/` (versions propres et annotées) intégrées au diaporama.
