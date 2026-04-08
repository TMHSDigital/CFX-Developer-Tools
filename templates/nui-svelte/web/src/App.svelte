<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { useNuiEvent, closeNui } from './nui-bridge';

  let visible = $state(false);

  let cleanup: (() => void) | undefined;

  onMount(() => {
    cleanup = useNuiEvent('open', () => {
      visible = true;
    });

    useNuiEvent('close', () => {
      visible = false;
    });

    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        visible = false;
        closeNui();
      }
    };
    document.addEventListener('keydown', handleKeydown);

    return () => {
      document.removeEventListener('keydown', handleKeydown);
    };
  });

  onDestroy(() => {
    cleanup?.();
  });
</script>

{#if visible}
  <div class="overlay">
    <div class="panel">
      <h1>My Resource</h1>
      <p>Svelte 5 NUI template</p>
      <button onclick={() => { visible = false; closeNui(); }}>Close</button>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
  }
  .panel {
    background: #1a1a2e;
    border-radius: 8px;
    padding: 2rem;
    min-width: 320px;
    text-align: center;
  }
  h1 { margin-bottom: 0.5rem; }
  button {
    margin-top: 1rem;
    padding: 0.5rem 1.5rem;
    border: none;
    border-radius: 4px;
    background: #e94560;
    color: #fff;
    cursor: pointer;
    font-size: 1rem;
  }
  button:hover { background: #c73a54; }
</style>
