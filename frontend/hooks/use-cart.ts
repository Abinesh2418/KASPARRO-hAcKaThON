"use client";

import { useState, useCallback } from "react";
import type { CartItem } from "@/types";
import { addToCart, removeFromCart, fetchCart } from "@/services/api";

export function useCart() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);

  const getUsername = (): string | null => {
    if (typeof window === "undefined") return null;
    try {
      const raw = localStorage.getItem("curio_user");
      if (!raw) return null;
      return JSON.parse(raw).username ?? null;
    } catch {
      return null;
    }
  };

  const loadCart = useCallback(async () => {
    const username = getUsername();
    if (!username) return;
    setLoading(true);
    const data = await fetchCart(username);
    setItems(data);
    setLoading(false);
  }, []);

  const add = useCallback(async (product: { id: string; title: string; price: number; images: string[]; }, size?: string) => {
    const username = getUsername();
    if (!username) return;
    const updated = await addToCart({
      username,
      product_id: product.id,
      title: product.title,
      price: product.price,
      image: product.images[0] ?? "",
      size: size ?? null,
    });
    setItems(updated);
  }, []);

  const remove = useCallback(async (productId: string) => {
    const username = getUsername();
    if (!username) return;
    const updated = await removeFromCart(productId, username);
    setItems(updated);
  }, []);

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return { items, loading, loadCart, add, remove, total };
}
