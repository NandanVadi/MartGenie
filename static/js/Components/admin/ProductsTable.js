import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Pencil, Trash2, Package } from 'lucide-react';

export default function ProductsTable({ products, onEdit, onDelete }) {
  const getCategoryBadge = (category) => {
    const colors = {
      groceries: 'bg-emerald-100 text-emerald-700',
      dairy: 'bg-blue-100 text-blue-700',
      beverages: 'bg-purple-100 text-purple-700',
      snacks: 'bg-amber-100 text-amber-700',
      household: 'bg-rose-100 text-rose-700',
      personal_care: 'bg-pink-100 text-pink-700',
      frozen: 'bg-cyan-100 text-cyan-700',
    };

    return (
      <Badge variant="secondary" className={colors[category] || 'bg-slate-100 text-slate-700'}>
        {category?.replace('_', ' ')}
      </Badge>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div className="p-4 md:p-6 border-b border-slate-100 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">Product Inventory</h3>
        <Badge variant="outline" className="bg-slate-50">
          {products.length} products
        </Badge>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50">
              <TableHead className="font-semibold">Product</TableHead>
              <TableHead className="font-semibold">Barcode</TableHead>
              <TableHead className="font-semibold">Category</TableHead>
              <TableHead className="font-semibold">Price</TableHead>
              <TableHead className="font-semibold">Stock</TableHead>
              <TableHead className="font-semibold text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {products.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8">
                  <Package className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                  <p className="text-slate-500">No products added yet</p>
                </TableCell>
              </TableRow>
            ) : (
              products.map((product) => (
                <TableRow key={product.id} className="hover:bg-slate-50">
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-slate-100 overflow-hidden flex-shrink-0">
                        {product.image_url ? (
                          <img 
                            src={product.image_url} 
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Package className="w-5 h-5 text-slate-400" />
                          </div>
                        )}
                      </div>
                      <span className="font-medium text-slate-800">{product.name}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-slate-600 text-sm">
                    {product.barcode}
                  </TableCell>
                  <TableCell>
                    {getCategoryBadge(product.category)}
                  </TableCell>
                  <TableCell className="font-semibold text-slate-800">
                    ₹{product.price?.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <span className={`font-medium ${
                      product.stock < 10 ? 'text-red-600' : 'text-emerald-600'
                    }`}>
                      {product.stock || 0}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button 
                        variant="ghost" 
                        size="icon"
                        className="h-8 w-8 text-slate-500 hover:text-slate-700"
                        onClick={() => onEdit?.(product)}
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                        onClick={() => onDelete?.(product)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}