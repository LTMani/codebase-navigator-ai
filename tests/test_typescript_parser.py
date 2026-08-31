import pytest
from app.parsers.typescript_parser import TypeScriptParser


def test_typescript_parser_interfaces_and_classes():
    code = """
import { useState, useEffect } from 'react';
import type { UserProfile } from './types';

export interface ProductPayload {
    id: string;
    name: string;
    price: number;
}

export type StatusType = 'active' | 'inactive';

export class OrderManager {
    private orders: Order[] = [];

    public async placeOrder(payload: ProductPayload): Promise<boolean> {
        console.log("Placing order", payload);
        return true;
    }
}

export const calculateDiscount = (price: number, discount: number = 0.1): number => {
    return price * (1 - discount);
};
"""
    parser = TypeScriptParser()
    res = parser.parse(code, "src/OrderManager.ts")

    assert res.language == "TypeScript"
    assert len(res.classes) == 1
    assert res.classes[0].name == "OrderManager"

    # Symbols check
    symbol_names = [s.name for s in res.symbols]
    assert "ProductPayload" in symbol_names
    assert "StatusType" in symbol_names
    assert "OrderManager" in symbol_names
    assert "calculateDiscount" in symbol_names

    # Imports check
    assert len(res.imports) == 2
    assert res.imports[0].module_name == "react"
