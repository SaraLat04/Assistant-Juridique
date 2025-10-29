import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatServiceService } from '../../services/chat-service.service';

interface HistoryItem {
  id: string;
  title: string;
  created_at: string;
  last_message?: any;
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
  selectedItemId: string | null = null;

  @Output() selectConversation = new EventEmitter<string>();

  constructor(private chatService: ChatServiceService) {}

  ngOnInit() {
    this.loadHistory();
  }

  async loadHistory() {
    try {
      const convs = await this.chatService.listConversations();
      this.historyItems = convs.map((c: any) => ({
        id: c.id,
        title: c.title || 'Conversation',
        created_at: c.created_at,
        last_message: c.last_message
      }));
    } catch (e) {
      console.warn('Impossible de charger l\'historique depuis le backend', e);
      this.historyItems = [];
    }
  }

  selectItem(id: string) {
    this.selectedItemId = id;
    this.selectConversation.emit(id);
  }

  async deleteItem(id: string, event: Event) {
    event.stopPropagation();
    // Pour l'instant on enlève côté UI seulement (backend: suppression non implémentée)
    this.historyItems = this.historyItems.filter(item => item.id !== id);
  }

  getRelativeTime(date: string): string {
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
    this.selectConversation.emit(null as any);
  }
}