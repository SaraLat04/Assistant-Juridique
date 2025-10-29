import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

interface HistoryItem {
  id: number;
  title: string;
  date: Date;
  preview: string;
}

@Component({
  selector: 'app-historique',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './historique.component.html',
  styleUrls: ['./historique.component.css']
})
export class HistoriqueComponent implements OnInit {
  historyItems: HistoryItem[] = [];
  selectedItemId: number | null = null;

  ngOnInit() {
    // Charger l'historique depuis localStorage ou votre service
    this.loadHistory();
  }

  loadHistory() {
    // Exemple de données - remplacez par votre logique
    // Vous pouvez charger depuis localStorage :
    const saved = localStorage.getItem('chat_history');
    if (saved) {
      this.historyItems = JSON.parse(saved);
    } else {
      // Données d'exemple
      this.historyItems = [
        {
          id: 1,
          title: 'Droits du locataire',
          date: new Date(Date.now() - 2 * 60 * 60 * 1000),
          preview: 'Quels sont les droits du locataire en cas de litige ?'
        },
        {
          id: 2,
          title: 'Contrat de travail',
          date: new Date(Date.now() - 24 * 60 * 60 * 1000),
          preview: 'Comment rédiger un contrat de travail conforme ?'
        },
        {
          id: 3,
          title: 'Création d\'entreprise',
          date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
          preview: 'Procédure pour créer une société SARL'
        }
      ];
    }
  }

  selectItem(id: number) {
    this.selectedItemId = id;
    // TODO: Émettre un événement ou appeler un service pour charger la conversation
    console.log('Conversation sélectionnée:', id);
  }

  deleteItem(id: number, event: Event) {
    event.stopPropagation();
    this.historyItems = this.historyItems.filter(item => item.id !== id);
    
    // Sauvegarder dans localStorage
    localStorage.setItem('chat_history', JSON.stringify(this.historyItems));
    
    if (this.selectedItemId === id) {
      this.selectedItemId = null;
    }
  }

  getRelativeTime(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - new Date(date).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return diffDays === 1 ? 'Hier' : `Il y a ${diffDays}j`;
    return new Date(date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  }

  newChat() {
    this.selectedItemId = null;
    // TODO: Émettre un événement pour démarrer une nouvelle conversation
    console.log('Nouvelle conversation');
  }

  // Méthode pour ajouter une conversation à l'historique
  addToHistory(title: string, preview: string) {
    const newItem: HistoryItem = {
      id: Date.now(),
      title: title,
      date: new Date(),
      preview: preview
    };
    
    this.historyItems.unshift(newItem); // Ajouter au début
    
    // Limiter à 50 conversations
    if (this.historyItems.length > 50) {
      this.historyItems = this.historyItems.slice(0, 50);
    }
    
    // Sauvegarder dans localStorage
    localStorage.setItem('chat_history', JSON.stringify(this.historyItems));
  }
}