import { describe, it, expect, vi } from 'vitest';
import { apiClient, createTaskFromPath, ensureBackendBase } from './api';

describe('API Client', () => {

  describe('ensureBackendBase', () => {
    it('should return default baseURL in non-Tauri environment', async () => {
      const baseURL = await ensureBackendBase();
      expect(baseURL).toBe('/api');
      expect(apiClient.defaults.baseURL).toBe('/api');
    });

    it('should cache the backend base promise', async () => {
      const base1 = await ensureBackendBase();
      const base2 = await ensureBackendBase();

      expect(base1).toBe(base2);
    });
  });

  describe('apiClient configuration', () => {
    it('should have correct default baseURL', () => {
      expect(apiClient.defaults.baseURL).toBe('/api');
    });

    it('should be an axios instance', () => {
      expect(apiClient).toBeDefined();
      expect(typeof apiClient.get).toBe('function');
      expect(typeof apiClient.post).toBe('function');
      expect(typeof apiClient.delete).toBe('function');
    });
  });

  describe('transcription language', () => {
    it('sends English when a task language is omitted', async () => {
      const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ data: { id: 'task-en' } });

      await expect(createTaskFromPath('C:\\recordings\\lecture.m4a')).resolves.toBe('task-en');

      expect(post).toHaveBeenCalledWith('/tasks/local', {
        path: 'C:\\recordings\\lecture.m4a',
        language: 'en',
      });
      post.mockRestore();
    });
  });
});
