/** Base entity with common fields */
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

/** Entity that supports soft deletion */
export interface SoftDeletableEntity extends BaseEntity {
  deletedAt: string | null;
}

/** Entity with audit trail */
export interface AuditableEntity extends BaseEntity {
  createdBy: string;
  updatedBy: string;
}
